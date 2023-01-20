""" Read pv generation functions """
import logging
from datetime import datetime, timezone
from typing import List, Optional, Union

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from pvsite_datamodel.sqlmodels import GenerationSQL, SiteSQL, DatetimeIntervalSQL, ClientSQL

logger = logging.getLogger(__name__)


def get_pv_generation(
    session: Session,
    start_utc: Optional[datetime] = None,
    end_utc: Optional[datetime] = None,
    client_names: Optional[List[str]] = None,
) -> Union[List[GenerationSQL]]:
    """
    Get the generation data
    :param session: database session
    :param end_utc: search filters < on 'datetime_utc'. Can be None
    :param start_utc: search filters >= on 'datetime_utc'. Can be None
    :param client_names: optional list of provider names
    :return: either list of pv yields, or pv systems
    """

    # start main query
    query = session.query(GenerationSQL)
    query = query.join(SiteSQL)
    query = query.join(ClientSQL)
    query = query.join(DatetimeIntervalSQL)

    # filter on start time
    if start_utc is not None:
        query = query.filter(DatetimeIntervalSQL.start_utc >= start_utc)

    # filter on end time
    if end_utc is not None:
        query = query.filter(DatetimeIntervalSQL.end_utc < end_utc)

    if client_names is not None:
        query = query.filter(ClientSQL.client_name.in_(client_names))

    # order by 'created_utc' desc, so we get the latest one
    query = query.order_by(
        SiteSQL.site_uuid,
        DatetimeIntervalSQL.start_utc,
    )

    # get all results
    generations: List[GenerationSQL] = query.all()

    return generations
