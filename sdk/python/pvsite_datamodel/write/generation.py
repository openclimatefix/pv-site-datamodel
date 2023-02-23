"""
Write helpers for the Generation table.
"""

import datetime as dt
import logging

import pandas as pd
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import Base, GenerationSQL

_log = logging.getLogger(__name__)


def _upsert(session: Session, table: Base, rows: list[dict]):
    """Upserts rows into table.

    This functions checks the primary keys, and if present, updates the row.
    :param session: sqlalchemy Session
    :param table: the table
    :param rows: the rows we are going to update
    """
    stmt = postgresql.insert(table.__table__)
    primary_key_names = [key.name for key in sa.inspect(table.__table__).primary_key]
    update_dict = {c.name: c for c in stmt.excluded if not c.primary_key}

    if not update_dict:
        raise ValueError("insert_or_update resulted in an empty update_dict")

    stmt = stmt.on_conflict_do_update(index_elements=primary_key_names, set_=update_dict)
    session.execute(stmt, rows)


def insert_generation_values(
    session: Session,
    df: pd.DataFrame,
):
    """Insert a dataframe of forecast values into the database.

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

    _upsert(session, GenerationSQL, generation_sqls)
