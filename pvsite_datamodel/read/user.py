import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import UserSQL, SiteGroupSQL

logger = logging.getLogger(__name__)


def get_user_by_email(session: Session, email: str):

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
