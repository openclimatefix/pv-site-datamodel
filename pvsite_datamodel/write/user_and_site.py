""" Tools for making fake users and sites in the database."""
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm.session import Session

from pvsite_datamodel.read import get_user_by_email
from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL, SiteGroupSQL, SiteSQL, UserSQL


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


# TODO move create_new site_function here.
#  For the moment, data folder in ocf-dashboard has code this function depends on and this
#  should probably be done in an new issue


def create_user(
    session: Session,
    email: str,
    site_group_name: str,
) -> UserSQL:
    """Create a user.

    :param session: database session
    :param email: email of user being created
    :param site_group: name of the site group this user will be part of
    """

    site_group = (
        session.query(SiteGroupSQL).filter(SiteGroupSQL.site_group_name == site_group_name).first()
    )

    user = UserSQL(email=email, site_group_uuid=site_group.site_group_uuid)

    session.add(user)
    site_group.users.append(user)
    session.commit()

    return user


# update functions for site and site group
def add_site_to_site_group(session: Session, site_uuid: str, site_group_name: str) -> SiteGroupSQL:
    """Add a site to a site group.

    NB: Sites can belong to many site groups.
    :param session: database session
    :param site_uuid: uuid of site
    :param site_group_name: name of site group
    """
    site_group = (
        session.query(SiteGroupSQL).filter(SiteGroupSQL.site_group_name == site_group_name).first()
    )

    site = session.query(SiteSQL).filter(SiteSQL.site_uuid == site_uuid).one()

    if site not in site_group.sites:
        site_group.sites.append(site)

    session.commit()

    return site_group.sites


# change site group for user
def change_user_site_group(session, email: str, site_group_name: str):
    """
    Change user to a specific site group name.

    :param session: the database session
    :param email: the email of the user
    """
    update_user_site_group(session=session, email=email, site_group_name=site_group_name)
    user = get_user_by_email(session=session, email=email)
    user_site_group = user.site_group.site_group_name
    user = user.email
    return user, user_site_group


def update_user_site_group(session: Session, email: str, site_group_name: str) -> UserSQL:
    """Change site group for user.

    :param session: database session
    :param email: email of user
    :param site_group_name: name of site group
    """
    site_group = (
        session.query(SiteGroupSQL).filter(SiteGroupSQL.site_group_name == site_group_name).first()
    )

    user = session.query(UserSQL).filter(UserSQL.email == email)

    user = user.update({"site_group_uuid": site_group.site_group_uuid})

    session.commit()


# delete functions for site, user, and site group
def delete_site(session: Session, site_uuid: str) -> SiteGroupSQL:
    """Delete a site group.

    :param session: database session
    :param site_uuid: unique identifier for site
    """
    site = session.query(SiteSQL).filter(SiteSQL.site_uuid == site_uuid).first()

    forecast_uuids = (
        session.query(ForecastSQL.forecast_uuid).filter(ForecastSQL.site_uuid == site_uuid).all()
    )

    forecast_uuids = [str(forecast_uuid[0]) for forecast_uuid in forecast_uuids]

    # get and delete all forecast values for site
    stmt = sa.delete(ForecastValueSQL).where(ForecastValueSQL.forecast_uuid.in_(forecast_uuids))
    session.execute(stmt)

    stmt_2 = sa.delete(ForecastSQL).where(ForecastSQL.forecast_uuid.in_(forecast_uuids))
    session.execute(stmt_2)

    # we decided not to delete generation data for the site
    # because it seems sensible to keep it for now

    session.delete(site)

    message = f"Site with site uuid {site.site_uuid} deleted successfully"

    session.commit()

    return message


# delete user
def delete_user(session: Session, email: str) -> UserSQL:
    """Delete a user.

    :param session: database session
    :param email: email of user being deleted
    """
    user = session.query(UserSQL).filter(UserSQL.email == email).first()

    session.delete(user)

    message = (
        f"User with email {user.email} and site_group_uuid "
        f"{user.site_group_uuid} deleted successfully"
    )

    session.commit()

    return message


# delete site group
def delete_site_group(session: Session, site_group_name: str) -> SiteGroupSQL:
    """Delete a site group.

    :param session: database session
    :param site_group_name: name of site group being deleted
    """
    site_group = (
        session.query(SiteGroupSQL).filter(SiteGroupSQL.site_group_name == site_group_name).first()
    )

    site_group_users = site_group.users

    if len(site_group_users) > 0:
        message = (
            f"Site group with name {site_group.site_group_name} and "
            f"site group uuid {site_group.site_group_uuid} has users and cannot be deleted."
        )
        return message

    session.delete(site_group)

    message = (
        f"Site group with name {site_group.site_group_name} "
        f"and site group uuid {site_group.site_group_uuid} deleted successfully."
    )

    session.commit()

    return message
