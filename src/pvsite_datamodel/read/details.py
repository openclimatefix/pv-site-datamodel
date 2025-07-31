"""
This module contains functions to get details from the database for a user or site group.

"""

import re
from typing import Dict, List

from pvsite_datamodel.read.user import get_user_by_email, get_site_group_by_name


def get_user_details(
    session, email: str
) -> tuple[List[Dict[str, str]], str, int]:
    """
    Get the user details from the database.

    Args:
        session: Database session
        email: User's email address

    Returns:
        tuple: (user_sites, user_site_group, user_site_count)
    """
    user_details = get_user_by_email(session=session, email=email)
    user_site_group = user_details.location_group.location_group_name
    user_site_count = len(user_details.location_group.locations)
    user_sites = [
        {
            "site_uuid": str(site.location_uuid),
            "client_site_id": str(site.client_location_id)
        }
        for site in user_details.location_group.locations
    ]
    return user_sites, user_site_group, user_site_count


def get_site_group_details(
    session, site_group_name: str
) -> tuple[List[Dict[str, str]], List[str]]:
    """
    Get the site group details from the database.

    Args:
        session: Database session
        site_group_name: Name of the site group

    Returns:
        tuple: (site_group_sites, site_group_users)
    """
    site_group = get_site_group_by_name(
        session=session, site_group_name=site_group_name
    )
    site_group_sites = [
        {
            "site_uuid": str(site.location_uuid),
            "client_site_id": str(site.client_location_id)
        }
        for site in site_group.locations
    ]
    site_group_users = [user.email for user in site_group.users]
    return site_group_sites, site_group_users


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
