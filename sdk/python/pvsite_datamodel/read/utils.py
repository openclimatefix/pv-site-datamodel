"""
Cross-package functions
"""

from datetime import datetime
from typing import Optional

from pvsite_datamodel.sqlmodels import DatetimeIntervalSQL
from sqlalchemy.orm import Query


def filter_query_by_datetime_interval(
    query: Query, start_utc: Optional[datetime] = None, end_utc: Optional[datetime] = None
) -> Query:
    """
    Applies a filter on the input query according to the Datetime Interval table.

    Ensure DatetimeIntervalSQL has been joined to query already
    :param query: The sqlalchemy query
    :param start_utc: search filters >= on 'start_utc'. Can be None
    :param end_utc: search filters < on 'end_utc'. Can be None
    :return: The sqlalchemy query
    """

    # filter on start time
    if start_utc is not None:
        query = query.filter(DatetimeIntervalSQL.start_utc >= start_utc)

    # filter on end time
    if end_utc is not None:
        query = query.filter(DatetimeIntervalSQL.end_utc < end_utc)

    return query
