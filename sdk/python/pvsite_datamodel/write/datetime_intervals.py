import datetime as dt
import uuid

from sqlalchemy import orm as sa_orm

from pvsite_datamodel import sqlmodels
from pvsite_datamodel.write.upsert import upsert
from pvsite_datamodel.write.utils import WrittenRow, FORECAST_TIMESPAN


def get_or_else_create_datetime_interval(
    session: sa_orm.Session, start_time: dt.datetime, end_time: dt.datetime = None
) -> tuple[sqlmodels.DatetimeIntervalSQL, list[WrittenRow]]:
    """
    Gets a DatetimeInterval from the DB by start time if it exists, otherwise it creates a new entry

    :param session: The SQLAlchemy session used for performing db updates
    :param start_time: The start time of the datetime interval
    :param end_time: The end time of the datetime interval. Optional, defaults to the start_time
    + FORECAST_TIMESPAN
    :return tuple(sqlmodels.DatetimeIntervalSQL, list[WrittenRow]): A tuple containing the existing
    or created DatetimeIntervalSQL object, and a list of WrittenRow objects dictating what was
    written to the DB
    """

    # End time defaults to the start time + FORECAST_TIMESPAN timedelta
    if end_time is None:
        end_time = start_time + FORECAST_TIMESPAN

    # Check if a datetime interval exists for the input times
    query = session.query(sqlmodels.DatetimeIntervalSQL)
    query = query.filter(sqlmodels.DatetimeIntervalSQL.start_utc == start_time)
    query = query.filter(sqlmodels.DatetimeIntervalSQL.end_utc == end_time)
    existing_interval: sqlmodels.DatetimeIntervalSQL = query.first()

    # If it does, fetch it's uuid
    if existing_interval is not None:
        return existing_interval, []

    # If it doesn't, create a new one
    else:
        datetime_interval: sqlmodels.DatetimeIntervalSQL = sqlmodels.DatetimeIntervalSQL(
            datetime_interval_uuid=uuid.uuid4(),
            start_utc=start_time,
            end_utc=end_time,
            created_utc=dt.datetime.now(tz=dt.timezone.utc),
        )
        written_rows = upsert(session, sqlmodels.DatetimeIntervalSQL, [datetime_interval.__dict__])
        return datetime_interval, written_rows