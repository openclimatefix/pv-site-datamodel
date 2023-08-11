""" Functions for reading user data from the database. """
import logging

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
