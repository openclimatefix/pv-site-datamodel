"""
Functions for writing to pvsite db
"""

import datetime as dt
import logging
import uuid

import dateutil.parser as dp
import numpy as np
import pandas as pd
import sqlalchemy.orm as sa_orm
from pvsite_datamodel import  sqlmodels

# Defines the length of time over which a forecast is valid
from pvsite_datamodel.write.datetime_intervals import get_or_else_create_datetime_interval
from pvsite_datamodel.write.upsert import upsert
from pvsite_datamodel.write.utils import WrittenRow
from pvsite_datamodel.read import get_site_from_uuid


def insert_forecast_values(
    session: sa_orm.Session, df_forecast_values: pd.DataFrame, forecast_version: str = "0.0.0"
) -> list[WrittenRow]:
    """
    Inserts a dataframe of forecast values into the database.

    :param session: sqlalchemy session for interacting with the database
    :param df_forecast_values: pandas dataframe with columns
    ["target_datetime_utc", "forecast_kw", "pv_uuid"]
    :param forecast_version: the version of the model used to create the forecast
    :return list[WrittenRow]: list of added rows to DB
    """

    # Track rows added to DB
    written_rows: list[WrittenRow] = []

    # Loop over all the unique sites that have got forecast values
    sites: np.ndarray = df_forecast_values["pv_uuid"].unique()
    sql_forecast_values = []
    for site_uuid in sites:

        # Check whether the site id exits in the table, otherwise return an error
        get_site_from_uuid(session=session, site_uuid=site_uuid)

        # Create a forcast (sequence) for the site, and write it to db
        forecast: sqlmodels.ForecastSQL = sqlmodels.ForecastSQL(
            forecast_uuid=uuid.uuid4(),
            site_uuid=site_uuid,
            created_utc=dt.datetime.now(tz=dt.timezone.utc),
            forecast_version=forecast_version,
        )
        newly_written_rows = upsert(session, sqlmodels.ForecastSQL, forecast.__dict__)
        written_rows.extend(newly_written_rows)

        # Get all dataframe forecast value entries for current site_uuid
        df_site: pd.DataFrame = df_forecast_values.loc[df_forecast_values["pv_uuid"] == site_uuid]

        # Filter the forecasted values by target_time
        target_times: np.ndarray = df_site["target_datetime_utc"].unique()

        # Print a warning if there are duplicate target_times for this site's forecast
        if len(target_times) != len(df_site):
            logging.warning(
                f"duplicate target times exist in forecast {forecast.forecast_uuid} "
                f"for site {site_uuid}"
            )

        # For each target time:
        for target_time in target_times:
            # Convert the target_time string to a datetime object
            target_time_as_datetime: dt.datetime = dp.isoparse(target_time)

            datetime_interval, newly_added_rows = get_or_else_create_datetime_interval(
                session=session, start_time=target_time_as_datetime
            )
            written_rows.extend(newly_added_rows)

            # For each entry with this targettime (there should only be one)
            df_target_entries: pd.DataFrame = df_site.loc[
                df_site["target_datetime_utc"] == target_time
            ]

            # Create a ForecastValueSQL object for each forecast value, and surface as dict
            # TODO there might be quicker ways to do this, like go from pandas straight to a dict
            sql_forecast_value =  sqlmodels.ForecastValueSQL(
                    forecast_uuid=forecast.forecast_uuid,
                    forecast_value_uuid=uuid.uuid4(),
                    datetime_interval_uuid=datetime_interval.datetime_interval_uuid,
                    created_utc=dt.datetime.now(tz=dt.timezone.utc),
                    forecast_generation_kw=df_target_entries.iloc[0]["forecast_kw"],
            ).__dict__
            sql_forecast_values.append(sql_forecast_value)

    # Save it to the db
    newly_added_rows = upsert(session, sqlmodels.ForecastValueSQL, sql_forecast_values)
    written_rows.extend(newly_added_rows)

    return written_rows


