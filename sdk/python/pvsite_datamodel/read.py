"""
Functions for reading to pvsite db
"""

import logging

from sqlalchemy.orm import Session
from pvsite_datamodel.sqlmodels import ClientSQL, SiteSQL

logger = logging.getLogger(__name__)


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

