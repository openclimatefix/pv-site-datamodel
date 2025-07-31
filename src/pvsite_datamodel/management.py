"""This module contains functions for managing site groups."""

import re
from typing import List, Dict, Any, Tuple

from pvsite_datamodel.read import (
    get_user_by_email,
    get_site_by_uuid,
    get_site_group_by_name,
)
from pvsite_datamodel.read.site import get_all_sites, get_site_by_client_site_id

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


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        bool: True if email is valid, False otherwise
    """
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    return False
