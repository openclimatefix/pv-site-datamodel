import datetime
from typing import List

import schema

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_psql
import sqlalchemy.orm as sa_orm
import pandas as pd
import dateutil.parser
import uuid


def upsert(session: sa_orm.Session, model: schema.Base, rows: List[dict]):
    """
    Upsert rows into model
    Insert or Update rows into model.
    This functions checks the primary keys, and if duplicate updates them.
    :param session: sqlalchemy Session
    :param model: the model
    :param rows: the rows we are going to update
    """
    table = model.__table__
    stmt = sa_psql.insert(table)
    primary_keys = [key.name for key in sa.inspect(table).primary_key]
    update_dict = {c.name: c for c in stmt.excluded if not c.primary_key}

    if not update_dict:
        raise ValueError("insert_or_update resulted in an empty update_dict")

    stmt = stmt.on_conflict_do_update(index_elements=primary_keys, set_=update_dict)
    session.execute(stmt, rows)


def upsert_forecast(session: sa_orm.Session, df: pd.DataFrame):
    """
    Upsert a forecast into forecast table. Errors if site does not exist in sites
    table. Populates forecast_values table with forecast values.
    :param df: pandas dataframe with columns ["target_datetime_utc", "forecast_kw", "pv_uuid"]
    """

    datetime_intervals = [ for target_datetime in df["target_datetime_utc"]]

def _generate_interval(target_datetime_utc: str) -> schema.DatetimeIntervals:
    start_time = dateutil.parser.isoparse(target_datetime_utc)

    return schema.DatetimeIntervals(
        uuid=uuid.uuid4(),
        start_utc=start_time,
        end_utc=start_time + datetime.timedelta(minutes=5) # Each forecast_value is for a time period of 5 mins,
    )
