"""Read functions for site group operations."""

from pvsite_datamodel.read import get_site_by_uuid
from pvsite_datamodel.read.site import (
    get_all_client_site_ids as _get_all_client_site_ids,
    get_all_site_uuids as _get_all_site_uuids,
)


def select_site_by_uuid(session, site_uuid: str) -> str:
    """
    Select a site by its UUID.

    Args:
        session: Database session
        site_uuid: UUID of the site to select

    Returns:
        str: The site UUID

    Raises:
        ValueError: If site with the given UUID is not found
    """
    try:
        site = get_site_by_uuid(session=session, site_uuid=site_uuid)
        return str(site.location_uuid)
    except Exception as err:
        raise ValueError(f"Site with UUID {site_uuid} not found") from err


def select_site_by_client_id(session, client_site_id: str) -> str:
    """
    Select a site by its client site ID.

    Args:
        session: Database session
        client_site_id: Client site ID

    Returns:
        str: The site UUID

    Raises:
        ValueError: If site with the given client site ID is not found
    """
    try:
        from pvsite_datamodel.sqlmodels import LocationSQL

        query = session.query(LocationSQL)
        query = query.filter(LocationSQL.client_location_id == client_site_id)
        site = query.first()
        if site is None:
            raise ValueError(f"Site with client ID {client_site_id} not found")
        return str(site.location_uuid)
    except Exception as err:
        if "not found" in str(err):
            raise err
        raise ValueError(f"Site with client ID {client_site_id} not found") from err


def get_all_site_uuids(session) -> list[str]:
    """
    Get all site UUIDs from the database.

    Args:
        session: Database session

    Returns:
        list: List of all site UUIDs as strings
    """
    return _get_all_site_uuids(session=session)


def get_all_client_site_ids(session) -> list[str]:
    """
    Get all client site IDs from the database.

    Args:
        session: Database session

    Returns:
        list: List of all client site IDs as strings
    """
    return _get_all_client_site_ids(session=session)
