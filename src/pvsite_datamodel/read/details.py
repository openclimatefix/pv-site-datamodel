"""
This module contains functions to get details from the database for a user, site or site group.

"""

import re
from typing import Dict, List, Any

from pvsite_datamodel.read import (
    get_user_by_email,
    get_site_by_uuid,
    get_site_group_by_name
)
from pvsite_datamodel.sqlmodels import LocationAssetType


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


def get_site_details(session, site_uuid: str) -> Dict[str, Any]:
    """
    Get the site details for one site.

    Args:
        session: Database session
        site_uuid: UUID of the site

    Returns:
        dict: Site details dictionary
    """
    site = get_site_by_uuid(session=session, site_uuid=site_uuid)

    if isinstance(site.asset_type, LocationAssetType):
        asset_type_value = str(site.asset_type.name.lower())
    else:
        asset_type_value = str(site.asset_type)

    site_details = {
        "site_uuid": str(site.location_uuid),
        "client_site_id": str(site.client_location_id),
        "client_site_name": str(site.client_location_name),
        "site_group_names": [
            site_group.location_group_name for site_group in site.location_groups
        ],
        "latitude": str(site.latitude),
        "longitude": str(site.longitude),
        "country": str(site.country),
        "asset_type": asset_type_value,
        "region": str(site.region),
        "DNO": str(site.dno),
        "GSP": str(site.gsp),
        "tilt": str(site.tilt),
        "orientation": str(site.orientation),
        "inverter_capacity_kw": f"{site.inverter_capacity_kw} kw",
        "module_capacity_kw": f"{site.module_capacity_kw} kw",
        "capacity": f"{site.capacity_kw} kw",
        "ml_model_uuid": str(site.ml_model_uuid),
        "date_added": site.created_utc.strftime("%Y-%m-%d"),
    }

    if site.ml_model_uuid is not None:
        site_details["ml_model_name"] = site.ml_model.name

    return site_details


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
