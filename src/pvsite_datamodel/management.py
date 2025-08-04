"""This module contains functions for managing site groups."""

from typing import List, Dict, Any, Tuple

from pvsite_datamodel.read import (
    get_user_by_email,
    get_site_by_uuid,
    get_site_group_by_name,
)
from pvsite_datamodel.read.site import get_all_sites

from pvsite_datamodel.write.user_and_site import (
    add_site_to_site_group,
    update_user_site_group,
)


def update_site_group(
    session, site_uuid: str, site_group_name: str
) -> Tuple[Any, List[Dict[str, str]], List[str]]:
    """
    Add a site to a site group.

    Args:
        session: Database session
        site_uuid: UUID of the site to add
        site_group_name: Name of the site group

    Returns:
        tuple: (site_group, site_group_sites, site_site_groups)
    """
    site_group = get_site_group_by_name(
        session=session, site_group_name=site_group_name
    )

    # Add site to site group
    add_site_to_site_group(
        session=session, site_uuid=site_uuid, site_group_name=site_group_name
    )

    # Get updated site group sites
    site_group_sites = [
        {
            "site_uuid": str(site.location_uuid),
            "client_site_id": str(site.client_location_id)
        }
        for site in site_group.locations
    ]

    # Get updated site's groups
    site = get_site_by_uuid(session=session, site_uuid=site_uuid)
    site_site_groups = [
        site_group.location_group_name
        for site_group in site.location_groups
    ]

    return site_group, site_group_sites, site_site_groups


def change_user_site_group(session, email: str, site_group_name: str) -> Tuple[str, str]:
    """
    Change user to a specific site group name.

    Args:
        session: Database session
        email: Email of the user
        site_group_name: Name of the site group

    Returns:
        tuple: (user_email, user_site_group)
    """
    update_user_site_group(
        session=session, email=email, site_group_name=site_group_name
    )
    user = get_user_by_email(session=session, email=email)
    user_site_group = user.location_group.location_group_name
    user_email = user.email
    return user_email, user_site_group


def add_all_sites_to_site_group(
    session, site_group_name: str = "ocf"
) -> Tuple[str, List[str]]:
    """
    Add all sites to a specified site group.

    Args:
        session: Database session
        site_group_name: Name of the site group (default: "ocf")

    Returns:
        tuple: (message, sites_added)
    """
    all_sites = get_all_sites(session=session)

    target_site_group = get_site_group_by_name(
        session=session, site_group_name=site_group_name
    )

    # Get existing site UUIDs in the group
    existing_site_uuids = [
        site.location_uuid for site in target_site_group.locations
    ]

    sites_added = []

    for site in all_sites:
        if site.location_uuid not in existing_site_uuids:
            target_site_group.locations.append(site)
            sites_added.append(str(site.location_uuid))
            session.commit()

    if len(sites_added) > 0:
        message = f"Added {len(sites_added)} sites to group {site_group_name}."
    else:
        message = f"There are no new sites to be added to {site_group_name}."

    return message, sites_added


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
    from pvsite_datamodel.read.site import get_all_site_uuids as _get_all_site_uuids
    return _get_all_site_uuids(session=session)


def get_all_client_site_ids(session) -> list[str]:
    """
    Get all client site IDs from the database.

    Args:
        session: Database session

    Returns:
        list: List of all client site IDs as strings
    """
    from pvsite_datamodel.read.site import get_all_client_site_ids as _get_all_client_site_ids
    return _get_all_client_site_ids(session=session)
    from pvsite_datamodel.read.site import get_all_site_uuids as _get_all_site_uuids
    return _get_all_site_uuids(session=session)


def get_all_client_site_ids(session) -> list[str]:
    """
    Get all client site IDs from the database.

    Args:
        session: Database session

    Returns:
        list: List of all client site IDs as strings
    """
    from pvsite_datamodel.read.site import get_all_client_site_ids as _get_all_client_site_ids
    return _get_all_client_site_ids(session=session)
