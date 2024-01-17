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
    # Check for duplicated (site_uuid, start_utc) entries.
    # TODO Should we have a unique constraint on those in the Database instead?
    sites_with_duplicate_times = df[df.duplicated(["site_uuid", "start_utc"])]["site_uuid"].unique()
    if len(sites_with_duplicate_times) > 0:
        for site_uuid in sites_with_duplicate_times:
            _log.warning(f'duplicate target datetimes for site "{site_uuid}"')

    # Build a list of the
    generation_sqls: list[dict] = []

    for _, row in df.iterrows():
        site_uuid = row["site_uuid"]
        start_utc = row["start_utc"]
        power_kw = row["power_kw"]

        # Create a GenerationSQL object for each generation, and surface as dict
        generation = GenerationSQL(
            site_uuid=site_uuid,
            generation_power_kw=power_kw,
            start_utc=start_utc,
            # TODO This is arbitrary and should be fixed
            # https://github.com/openclimatefix/pv-site-datamodel/issues/52
            end_utc=start_utc + dt.timedelta(minutes=5),
        ).__dict__

        generation_sqls.append(generation)

    _insert_do_nothing_on_conflict(session, GenerationSQL, generation_sqls)
