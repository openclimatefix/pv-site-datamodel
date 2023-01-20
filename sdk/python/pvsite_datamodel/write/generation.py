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
from pvsite_datamodel.sqlmodels import GenerationSQL

# Defines the length of time over which a forecast is valid
from pvsite_datamodel.write.datetime_intervals import get_or_else_create_datetime_interval
from pvsite_datamodel.write.upsert import upsert
from pvsite_datamodel.write.utils import WrittenRow
from pvsite_datamodel.read import get_site_from_uuid



def insert_generation_values(
    session: sa_orm.Session, generation_values_df: pd.DataFrame,
) -> list[WrittenRow]:
    """
    Inserts a dataframe of forecast values into the database.

    :param session: sqlalchemy session for interacting with the database
    :param generation_values_df: pandas dataframe with columns
    ["start_datetime_utc", "power_kw", "pv_uuid"]
    :return list[WrittenRow]: list of added rows to DB
    """

    # Track rows added to DB
    written_rows: list[WrittenRow] = []

    # Loop over all the unique sites that have got forecast values
    site_uuids: np.ndarray = generation_values_df["site_uuid"].unique()
    generation_sqls = []
    for site_uuid in site_uuids:

        # Check whether the site id exits in the table, otherwise return an error
        get_site_from_uuid(session=session, site_uuid=site_uuid)

        # Get all dataframe forecast value entries for current site_uuid
        df_site: pd.DataFrame = generation_values_df.loc[generation_values_df["site_uuid"] == site_uuid]

        # Filter the forecasted values by target_time
        start_datetimes: np.ndarray = df_site["start_datetime_utc"].unique()

        # Print a warning if there are duplicate target_times for this site's forecast
        if len(start_datetimes) != len(df_site):
            logging.warning(
                f"duplicate target datetimes "
                f"for site {site_uuid}"
            )

        # For each target time:
        for start_datetime in start_datetimes:

            datetime_interval, newly_added_rows = get_or_else_create_datetime_interval(
                session=session, start_time=pd.to_datetime(start_datetime)
            )
            written_rows.extend(newly_added_rows)

            # For each entry with this target time:
            df_target_entries: pd.DataFrame = df_site.loc[
                df_site["start_datetime_utc"] == start_datetimes
            ]

            # Create a GenerationSQL object for each generation, and surface as dict
            generation = GenerationSQL(
                site_uuid=site_uuid,
                generation_uuid=uuid.uuid4(),
                power_kw=df_target_entries.iloc[0].power_kw,
                datetime_interval_uuid=datetime_interval.datetime_interval_uuid,
            ).__dict__
            generation_sqls.append(generation)

        # Save it to the db
        newly_added_rows = upsert(session, GenerationSQL, generation_sqls)
        written_rows.extend(newly_added_rows)

    return written_rows


