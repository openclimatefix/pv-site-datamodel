"""Functions for reading to pvsite db."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from pvsite_datamodel.pydantic_models import LatitudeLongitudeLimits
from pvsite_datamodel.sqlmodels import (
    ClientSQL,
    LocationGroupLocationSQL,
    LocationGroupSQL,
    LocationSQL,
    UserSQL,
)

logger = logging.getLogger(__name__)


def get_site_by_uuid(session: Session, site_uuid: str) -> LocationSQL:
    """Get site object from uuid.

    Raise error if site does not exist.
    :param session: database sessions
    :param site_uuid: the site uuid
    :return: the site object
    """
    query = session.query(LocationSQL)
    query = query.filter(LocationSQL.location_uuid == site_uuid)
    existing_site: Optional[LocationSQL] = query.first()
    if existing_site is None:
        raise KeyError(f"Location uuid {site_uuid} not found in locations table")

    return existing_site


def get_site_by_client_site_id(
    session: Session, client_name: str, client_site_id: int
) -> LocationSQL:
    """Get site from client name and client site id.

    :param session: database sessions
    :param client_name: client name
    :param client_site_id: client's id of site
    :return: site object, or None
    """
    logger.debug(f"Getting {client_name}'s site {client_site_id}")

    # start main query
    query = session.query(LocationSQL)

    # start main query
    query = query.filter(LocationSQL.client_location_name == client_name)

    # select the correct client site id
    query = query.filter(LocationSQL.client_location_id == client_site_id)

    # get first result (should only be one site)
    site: Optional[LocationSQL] = query.first()

    if site is None:
        raise KeyError(f"Could not find location {client_site_id} from client {client_name}")

    return site


def get_site_by_client_site_name(
    session: Session, client_name: str, client_site_name: str
) -> LocationSQL:
    """Get site from client name and client site id.

    :param session: database sessions
    :param client_name: client name
    :param client_site_name: client's name of site
    :return: site object, or None
    """
    logger.debug(f"Getting {client_name}'s site {client_site_name}")

    # start main query
    query = session.query(LocationSQL)

    # select the correct client site name
    query = query.filter(LocationSQL.client_location_name == client_site_name)

    # get first result (should only be one site)
    site: Optional[LocationSQL] = query.first()

    if site is None:
        raise Exception(f"Could not find site {client_site_name} from client {client_name}")

    return site


def get_all_sites(session: Session) -> List[LocationSQL]:
    """Get all sites from the sites table.

    :param session: database session
    :return: site object
    """
    logger.debug("Getting all sites")

    # start main query
    query = session.query(LocationSQL)

    # order by uuuid
    query = query.order_by(LocationSQL.location_uuid)

    # get all results
    sites = query.all()

    logger.debug(f"Found {len(sites)} sites")

    return sites


def get_sites_by_country(
    session: Session, country: str, client_name: Optional[str] = None
) -> List[LocationSQL]:
    """Get sites for specific country from the sites table.

    :param session: database session
    :param country: country name
    :param client_name: optional client string, we search this in the 'client_site_name'.
    :return: site object
    """
    logger.debug(f"Getting sites by country={country}")

    # start main query
    query = session.query(LocationSQL)

    # filter by country
    query = query.filter(LocationSQL.country == country)

    # filter by client string
    # This could cause an issue if client_a's name is in the site of clients_b.
    # We could make a new Client table and join it with sites
    # https://github.com/openclimatefix/pv-site-datamodel/issues/148
    if client_name is not None:
        query = query.filter(LocationSQL.client_location_name.like(f"%{client_name}%"))

    # order by uuuid
    query = query.order_by(LocationSQL.location_uuid)

    # get all results
    sites = query.all()

    logger.debug(f"Found {len(sites)} sites")

    return sites


def get_sites_from_user(session, user, lat_lon_limits: Optional[LatitudeLongitudeLimits] = None):
    """
    Get the sites for a user.

    Option to filter on latitude longitude max and min
    """

    # get sites and filter if required
    if lat_lon_limits is not None:
        # make query
        query = session.query(LocationSQL)

        # join to Usersql through site groups
        query = query.join(LocationGroupLocationSQL)
        query = query.join(LocationGroupSQL)
        query = query.join(UserSQL)

        # filter on user on lat lon limits
        query = query.filter(LocationSQL.latitude <= lat_lon_limits.latitude_max)
        query = query.filter(LocationSQL.latitude >= lat_lon_limits.latitude_min)
        query = query.filter(LocationSQL.longitude <= lat_lon_limits.longitude_max)
        query = query.filter(LocationSQL.longitude >= lat_lon_limits.longitude_min)

        # query db
        sites = query.all()

    else:
        sites = user.location_group.locations
    return sites


def get_sites_by_client_name(session: Session, client_name: str) -> List[LocationSQL]:
    """Get sites from client name.

    :param session: database session
    :param client_name: client name
    :return: list of site objects
    """
    logger.debug(f"Getting {client_name}'s sites")

    # start main query
    query = session.query(LocationSQL)

    # join the Client table
    query = query.join(ClientSQL)

    # order by uuuid
    query = query.order_by(LocationSQL.location_uuid)

    # select the sites related to the client name
    query = query.filter(ClientSQL.client_name == client_name)

    # get all results
    sites: Optional[List[LocationSQL]] = query.all()

    if len(sites) == 0:
        raise Exception(f"Could not find locations from client {client_name}")

    return sites
