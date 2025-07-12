"""
Write helpers for the Generation table.
"""

import datetime as dt
import logging

import pandas as pd
from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import GenerationSQL
from pvsite_datamodel.write.utils import _insert_do_nothing_on_conflict

_log = logging.getLogger(__name__)


def insert_generation_values(
    session: Session,
    df: pd.DataFrame,
):
    """Insert a dataframe of generation values into the database.

    :param session: sqlalchemy session for interacting with the database
    :param df: dataframe with the data to insert
    """

    # rename site_uuid to location_uuid
    if "site_uuid" in df.columns and "location_uuid" not in df.columns:
        df.rename(columns={"site_uuid": "location_uuid"}, inplace=True)

    # Check for duplicated (site_uuid, start_utc) entries.
    # TODO Should we have a unique constraint on those in the Database instead?
    duplicates = df[df.duplicated(["location_uuid", "start_utc"])]
    sites_with_duplicate_times = duplicates["location_uuid"].unique()
    if len(sites_with_duplicate_times) > 0:
        for site_uuid in sites_with_duplicate_times:
            _log.warning(f'duplicate target datetimes for site "{site_uuid}"')

    # Build a list of the
    generation_sqls: list[dict] = []

    for _, row in df.iterrows():
        location_uuid = row["location_uuid"]
        start_utc = row["start_utc"]
        power_kw = row["power_kw"]
        end_utc = row.get("end_utc", default=start_utc + dt.timedelta(minutes=5))

        # Create a GenerationSQL object for each generation, and surface as dict
        generation = GenerationSQL(
            location_uuid=location_uuid,
            generation_power_kw=power_kw,
            start_utc=start_utc,
            # TODO This is arbitrary and should be fixed
            # https://github.com/openclimatefix/pv-site-datamodel/issues/52
            end_utc=end_utc,
        ).__dict__

        generation_sqls.append(generation)

    _insert_do_nothing_on_conflict(session, GenerationSQL, generation_sqls)
