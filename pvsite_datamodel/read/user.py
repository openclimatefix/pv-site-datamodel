""" Functions for reading user data from the database. """
import logging
from typing import List

from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import SiteGroupSQL, UserSQL

logger = logging.getLogger(__name__)


def get_user_by_email(session: Session, email: str):
    """
    Get user by email. If user does not exist, make one.

    :param session: database session
    :param email: email of user
    :return: user object
    """

    user = session.query(UserSQL).filter(UserSQL.email == email).first()

    if user is None:
        logger.info(f"User with email {email} not found, so making one")

        # making a new site group
        site_group = SiteGroupSQL(site_group_name=f"site_group_for_{email}")
        session.add(site_group)
        session.commit()

        # make a new user
        user = UserSQL(email=email, site_group_uuid=site_group.site_group_uuid)
        session.add(user)
        session.commit()

    return user


# get all users
def get_all_users(session: Session) -> List[UserSQL]:
    """
    Get all users from the database.

    :param session: database session
    """
    query = session.query(UserSQL)

    query = query.order_by(UserSQL.email.asc())

    users = query.all()

    return users


def get_site_group_by_name(session: Session, site_group_name: str):
    """
    Get site group by name. If site group does not exist, make one.

    :param session: database session
    :param site_group_name: name of site group
    :return: site group object
    """

    site_group = (
        session.query(SiteGroupSQL).filter(SiteGroupSQL.site_group_name == site_group_name).first()
    )

    if site_group is None:
        logger.info(f"Site group with name {site_group_name} not found, so making one")

        # make a new site group
        site_group = SiteGroupSQL(site_group_name=site_group_name)
        session.add(site_group)
        session.commit()

    return site_group


# get all site groups
def get_all_site_groups(session: Session) -> List[SiteGroupSQL]:
    """
    Get all site groups from the database.

    :param session: database session
    """
    query = session.query(SiteGroupSQL)

    query = query.order_by(SiteGroupSQL.site_group_name.asc())

    site_groups = query.all()

    return site_groups
