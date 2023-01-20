"""
Functions for reading to pvsite db
"""

import logging

from sqlalchemy.orm import Session
from pvsite_datamodel.sqlmodels import ClientSQL, SiteSQL

logger = logging.getLogger(__name__)


def get_site_from_uuid(session: Session, site_uuid: str):
    """
    Get site object from uuid.

    Raise error if site does not exists

    :param session: database sessions
    :param site_uuid: the site uuid
    :return: the site object
    """
    query = session.query(SiteSQL)
    query = query.filter(SiteSQL.site_uuid == site_uuid)
    existing_site: SiteSQL = query.first()
    if existing_site is None:
        raise KeyError(f"Site uuid {site_uuid} not found in sites table")

    return existing_site


def get_site(
    session: Session, client_name: str, client_id: str
) -> SiteSQL:
    """
    Get site from client name and client id

    :param session: database sessions
    :param client_name: client name
    :param client_id: client id
    :return: site object
    """

    logger.debug(f'Getting site for {client_name=} and {client_id=}')

    # start main query
    query = session.query(SiteSQL)
    query = query.join(ClientSQL)

    # select the correct client id
    query = query.filter(SiteSQL.client_site_id == client_id)

    # filter on client_name
    query = query.filter(ClientSQL.client_name == client_name)

    # get all results
    site = query.first()

    if site is None:
        raise Exception(f"Could not find site with {client_id=} and {client_name=}")

    return site

