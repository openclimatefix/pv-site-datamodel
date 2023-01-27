"""Read pv generation functions."""
import logging
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session, contains_eager

from pvsite_datamodel.sqlmodels import ClientSQL, DatetimeIntervalSQL, GenerationSQL, SiteSQL

from .utils import filter_query_by_datetime_interval

logger = logging.getLogger(__name__)


def get_pv_generation_by_client(
    session: Session,
    start_utc: Optional[datetime] = None,
    end_utc: Optional[datetime] = None,
    client_names: Optional[List[str]] = None,
) -> List[GenerationSQL]:
    """Get the generation data by client.

    :param session: database session
    :param end_utc: search filters < on 'datetime_utc'. Can be None
    :param start_utc: search filters >= on 'datetime_utc'. Can be None
    :param client_names: optional list of provider names
    :return:list of pv yields.
    """
    # start main query
    query = session.query(GenerationSQL)
    query = query.join(SiteSQL)
    query = query.join(ClientSQL)
    query = query.join(DatetimeIntervalSQL)

    # Filter by time interval
    query = filter_query_by_datetime_interval(query=query, start_utc=start_utc, end_utc=end_utc)

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


def get_pv_generation_by_sites(
    session: Session,
    start_utc: Optional[datetime] = None,
    end_utc: Optional[datetime] = None,
    site_uuids: Optional[List[uuid.UUID]] = None,
) -> List[GenerationSQL]:
    """Get the generation data by site.

    :param session: database session
    :param start_utc: search filters >= on 'datetime_utc'
    :param end_utc: search fileters < on 'datetime_utc'
    :param site_uuids: optional list of site uuids
    :return: list of pv yields
    """
    # start main query
    query = session.query(GenerationSQL)
    query = query.join(SiteSQL)
    query = query.join(DatetimeIntervalSQL)

    # Filter by time interval
    query = filter_query_by_datetime_interval(query=query, start_utc=start_utc, end_utc=end_utc)

    if site_uuids is not None:
        query = query.filter(SiteSQL.site_uuid.in_(site_uuids))

    # Order by 'created_utc' desc
    query = query.order_by(SiteSQL.site_uuid, DatetimeIntervalSQL.start_utc)

    # make sure this is all loaded
    query = query.options(contains_eager(GenerationSQL.datetime_interval)).populate_existing()
    query = query.options(contains_eager(GenerationSQL.site)).populate_existing()

    # get all results
    generations: List[GenerationSQL] = query.all()

    return generations
