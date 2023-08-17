""" Tools for making fake users and sites in the database."""
from datetime import datetime, timezone

from pvsite_datamodel.sqlmodels import SiteGroupSQL, SiteSQL, UserSQL


def make_site(db_session, ml_id=1):
    """Make a site.

    This is mainly used for testing purposes.
    """

    site = SiteSQL(
        client_site_id=1,
        latitude=51,
        longitude=3,
        capacity_kw=4,
        inverter_capacity_kw=4,
        module_capacity_kw=4.3,
        created_utc=datetime.now(timezone.utc),
        ml_id=ml_id,
    )
    db_session.add(site)
    db_session.commit()

    return site


def make_site_group(db_session, site_group_name="test_site_group"):
    """Make a site group.

    This is mainly used for testing purposes.
    """
    # create site group
    site_group = SiteGroupSQL(site_group_name=site_group_name)
    db_session.add(site_group)
    db_session.commit()

    return site_group


def make_user(db_session, email, site_group):
    """Make a user.

    This is mainly used for testing purposes.
    """
    # create a user
    user = UserSQL(email=email, site_group_uuid=site_group.site_group_uuid)
    db_session.add(user)
    db_session.commit()

    return user
