"""Functions for reading to pvsite db."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import ClientSQL, SiteSQL

logger = logging.getLogger(__name__)


def get_site_by_uuid(session: Session, site_uuid: str) -> SiteSQL:
    """Get site object from uuid.

    Raise error if site does not exist.
    :param session: database sessions
    :param site_uuid: the site uuid
    :return: the site object
    """
    query = session.query(SiteSQL)
    query = query.filter(SiteSQL.site_uuid == site_uuid)
    existing_site: Optional[SiteSQL] = query.first()
    if existing_site is None:
        raise KeyError(f"Site uuid {site_uuid} not found in sites table")

    return existing_site


def get_site_by_client_site_id(session: Session, client_name: str, client_site_id: int) -> SiteSQL:
    """Get site from client name and client site id.

    :param session: database sessions
    :param client_name: client name
    :param client_site_id: client's id of site
    :return: site object, or None
    """
    logger.debug(f"Getting {client_name}'s site {client_site_id}")

    # start main query
    query = session.query(SiteSQL)
    query = query.join(ClientSQL)

    # select the correct client site id
    query = query.filter(SiteSQL.client_site_id == client_site_id)

    # filter on client_name
    query = query.filter(ClientSQL.client_name == client_name)

    # get first result (should only be one site)
    site: Optional[SiteSQL] = query.first()

    if site is None:
        raise Exception(f"Could not find site {client_site_id} from client {client_name}")

    return site


def get_site_by_client_site_name(
    session: Session, client_name: str, client_site_name: str
) -> SiteSQL:
    """Get site from client name and client site id.

    :param session: database sessions
    :param client_name: client name
    :param client_site_name: client's name of site
    :return: site object, or None
    """
    logger.debug(f"Getting {client_name}'s site {client_site_name}")

    # start main query
    query = session.query(SiteSQL)
    query = query.join(ClientSQL)

    # select the correct client site name
    query = query.filter(SiteSQL.client_site_name == client_site_name)

    # filter on client_name
    query = query.filter(ClientSQL.client_name == client_name)

    # get first result (should only be one site)
    site: Optional[SiteSQL] = query.first()

    if site is None:
        raise Exception(f"Could not find site {client_site_name} from client {client_name}")

    return site


def get_all_sites(session: Session) -> List[SiteSQL]:
    """Get all sites from the sites table.

    :param session: database sessions
    :return: site object
    """
    logger.debug("Getting all sites")

    # start main query
    query = session.query(SiteSQL)

    # get all results
    sites = query.all()

    logger.debug(f"Found {len(sites)} sites")

    return sites
