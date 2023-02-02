"""Functions for writing to pvsite db."""

import datetime as dt
import logging
import uuid

import numpy.typing as npt
import pandas as pd
import sqlalchemy.orm as sa_orm

from pvsite_datamodel.read.site import get_site_by_uuid
from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL
from pvsite_datamodel.write.datetime_intervals import get_or_else_create_datetime_interval
from pvsite_datamodel.write.utils import WrittenRow


def insert_forecast_values(
    session: sa_orm.Session, df_forecast_values: pd.DataFrame, forecast_version: str = "0.0.0"
) -> list[WrittenRow]:
    """Insert a dataframe of forecast values into the database.

    :param session: sqlalchemy session for interacting with the database
    :param df_forecast_values: pandas dataframe with columns
        ["target_start_utc", "target_end_utc", "forecast_kw", "pv_uuid"]
    :param forecast_version: the version of the model used to create the forecast
    :return list[WrittenRow]: list of added rows to DB
    """
    # Track rows added to DB
    written_rows: list[WrittenRow] = []

    # Loop over all the unique sites that have got forecast values
    sites: npt.ndarray[uuid.UUID] = df_forecast_values["pv_uuid"].unique()

    for site_uuid in sites:
        # Check whether the site id exits in the table, otherwise return an error
        get_site_by_uuid(session=session, site_uuid=site_uuid)

        # Create a forcast (sequence) for the site, and write it to db
        forecast = ForecastSQL(
            # Explicitely setting the UUID because we need it for ForecastValueSQL.
            forecast_uuid=uuid.uuid4(),
            site_uuid=site_uuid,
            created_utc=dt.datetime.now(tz=dt.timezone.utc),
            forecast_version=forecast_version,
        )
        session.add(forecast)
        written_rows.append(forecast)

        # Get all dataframe forecast value entries for current site_uuid
        df_site: pd.DataFrame = df_forecast_values.loc[
            df_forecast_values["pv_uuid"] == site_uuid
        ]

        # Print a warning if there are duplicate target_times for this site's forecast
        if len(df_site["target_start_utc"].unique()) != len(df_site):
            logging.warning(
                f"duplicate target times exist in forecast {forecast.forecast_uuid} "
                f"for site {site_uuid}"
            )

        # For each target time:
        for _, row in df_site.iterrows():
            datetime_interval, newly_added_rows = get_or_else_create_datetime_interval(
                session=session,
                start_time=row["target_start_utc"],
                end_time=row["target_end_utc"],
            )
            written_rows.extend(newly_added_rows)

            sql_forecast_value = ForecastValueSQL(
                forecast_uuid=forecast.forecast_uuid,
                datetime_interval_uuid=datetime_interval.datetime_interval_uuid,
                created_utc=dt.datetime.now(tz=dt.timezone.utc),
                forecast_generation_kw=row["forecast_kw"],
            )
            session.add(sql_forecast_value)
            written_rows.append(sql_forecast_value)

    return written_rows
