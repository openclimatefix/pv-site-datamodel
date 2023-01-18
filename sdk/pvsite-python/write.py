import typing

import schema
import uuid

import datetime as dt
import numpy as np
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_psql
import sqlalchemy.orm as sa_orm
import pandas as pd
import dateutil.parser as dp

# Defines the length of time over which a forecast is valid
FORECAST_TIMESPAN = dt.timedelta(minutes=5)


class WrittenRow(typing.NamedTuple):
    """
    Defines a write to the Database
    """
    table: schema.Base
    pk_value: str


def upsert(session: sa_orm.Session, table: schema.Base, rows: list[dict]) -> list[WrittenRow]:
    """
    Upsert rows into table
    Insert or Update rows into table.
    This functions checks the primary keys, and if duplicate updates them.
    :param session: sqlalchemy Session
    :param table: the table
    :param rows: the rows we are going to update
    :return list[WrittenRow]: A list of WrittenRow objects containing the table and primary key values that have been
    written
    """
    stmt = sa_psql.insert(table.__table__)
    primary_key_names = [key.name for key in sa.inspect(table.__table__).primary_key]
    update_dict = {c.name: c for c in stmt.excluded if not c.primary_key}

    if not update_dict:
        raise ValueError("insert_or_update resulted in an empty update_dict")

    stmt = stmt.on_conflict_do_update(index_elements=primary_key_names, set_=update_dict)
    session.execute(stmt, rows)
    session.commit()

    return [
        WrittenRow(
            table=table,
            pk_value=row[primary_key_names[0]]
        ) for row in rows]


def insert_forecast_values(session: sa_orm.Session, df: pd.DataFrame) -> int:
    """
    Inserts a dataframe of forecast values into the database.
    :param session: sqlalchemy session for interacting with the database
    :param df: pandas dataframe with columns ["target_datetime_utc", "forecast_kw", "pv_uuid"]
    :return int: num added rows to DB
    """

    # Track rows added to DB
    written_rows: list[WrittenRow] = []

    # Loop over all the unique sites that have got forecast values
    sites: np.ndarray = df["pv_uuid"].unique()
    for site_uuid in sites:

        # Check whether the site id exits in the table, otherwise return an error
        # TODO

        # Create a forcast (sequence) for the site
        forecast: schema.ForecastSQL = schema.ForecastSQL(
            forecast_uuid=uuid.uuid4(),
            site_uuid=site_uuid,
            created_utc=dt.datetime.now(tz=dt.timezone.utc),
            forecast_version="0.0.0")

        # Get all dataframe forecast value entries for current site_uuid
        df_site: pd.DataFrame = df.loc[df["pv_uuid"] == site_uuid]

        # Filter the forecasted values by target_time
        target_times: np.ndarray = df_site["target_datetime_utc"].unique()

        # For each target time:
        for target_time in target_times:
            # Convert the target_time string to a datetime object
            target_time_as_datetime: dt.datetime = dp.isoparse(target_time)

            datetime_interval, newly_added_rows = get_or_else_create_datetime_interval(session=session,
                                                                                       start_time=target_time_as_datetime)
            written_rows.extend(newly_added_rows)

            # For each entry with this targettime:
            df_target_entries: pd.DataFrame = df.loc[df_site["target_datetime_utc"] == target_time]

            # Create a ForecastValueSQL object for each forecast value, and surface as dict
            forecast_values = [schema.ForecastValueSQL(
                forecast_uuid=forecast.forecast_uuid,
                forecast_value_uuid=uuid.uuid4(),
                datetime_interval_uuid=datetime_interval.datetime_interval_uuid,
                created_utc=dt.datetime.now(tz=dt.timezone.utc),
                forecast_generation_kw=generation_value,
            ).__dict__ for generation_value in df_target_entries["forecast_kw"]]

            # Save it to the db
            newly_added_rows = upsert(session, schema.ForecastValueSQL, forecast_values)
            written_rows.extend(newly_added_rows)

    return written_rows


def get_or_else_create_datetime_interval(session: sa_orm.Session, start_time: dt.datetime,
                                         end_time: dt.datetime = None) -> tuple[
    schema.DatetimeIntervalSQL, list[WrittenRow]]:
    """
    Gets a DatetimeInterval from the DB by start time if it exists, otherwise it creates a new entry
    :param session: The SQLAlchemy session used for performing db updates
    :param start_time: The start time of the datetime interval
    :param end_time: The end time of the datetime interval. Optional, defaults to the start_time + FORECAST_TIMESPAN
    :return tuple(schema.DatetimeIntervalSQL, list[WrittenRow]): A tuple containing the existing or created
    DatetimeIntervalSQL object, and a list of WrittenRow objects dictating what was written to the DB
    """

    # End time defaults to the start time + FORECAST_TIMESPAN timedelta
    if end_time is None:
        end_time = start_time + FORECAST_TIMESPAN

    # Check if a datetime interval exists for the input times
    query = session.query(schema.DatetimeIntervalSQL)
    query = query.filter(schema.DatetimeIntervalSQL.start_utc == start_time)
    query = query.filter(schema.DatetimeIntervalSQL.end_utc == end_time)
    existing_interval: schema.DatetimeIntervalSQL = query.first()

    # If it does, fetch it's uuid
    if existing_interval is not None:
        return existing_interval, []

    # If it doesn't, create a new one
    else:
        datetime_interval: schema.DatetimeIntervalSQL = schema.DatetimeIntervalSQL(
            datetime_interval_uuid=uuid.uuid4(),
            start_utc=start_time,
            end_utc=end_time,
            created_utc=dt.datetime.now(tz=dt.timezone.utc)
        )
        written_rows = upsert(session, schema.DatetimeIntervalSQL, [datetime_interval.__dict__])
        return datetime_interval, written_rows
