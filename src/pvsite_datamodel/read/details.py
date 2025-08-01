"""
This module contains functions to get details from the database for a user or site group.

"""

import re
from typing import Dict, List

from pvsite_datamodel.read.user import get_user_by_email, get_site_group_by_name
from pvsite_datamodel.read.site import get_site_by_uuid


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


def get_site_details(session, site_uuid: str) -> Dict[str, str]:
    """
    Get site details from the database.

    Args:
        session: Database session
        site_uuid: UUID of the site to get details for

    Returns:
        dict: Dictionary containing site details
    """
    site = get_site_by_uuid(session=session, site_uuid=site_uuid)

    # Convert asset type enum to string if it's an enum
    if hasattr(site.asset_type, 'name'):
        asset_type_str = site.asset_type.name
    else:
        asset_type_str = str(site.asset_type)

    # Get ML model name if available
    ml_model_name = site.ml_model.name if site.ml_model else None

    # Format capacity with units
    capacity_str = f"{site.capacity_kw} kw" if site.capacity_kw else None

    site_details = {
        "site_uuid": str(site.location_uuid),
        "client_site_id": str(site.client_location_id),
        "client_site_name": str(site.client_location_name) if site.client_location_name else None,
        "latitude": site.latitude,
        "longitude": site.longitude,
        "country": site.country,
        "asset_type": asset_type_str,
        "region": site.region,
        "dno": site.dno,
        "gsp": site.gsp,
        "tilt": site.tilt,
        "orientation": site.orientation,
        "inverter_capacity_kw": site.inverter_capacity_kw,
        "module_capacity_kw": site.module_capacity_kw,
        "capacity": capacity_str,
        "ml_model_name": ml_model_name,
        "created_utc": site.created_utc,
        "site_groups": [group.location_group_name for group in site.location_groups],
    }

    return site_details
