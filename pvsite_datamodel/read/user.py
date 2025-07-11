""" Functions for reading user data from the database. """

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session, contains_eager

from pvsite_datamodel.sqlmodels import APIRequestSQL, LocationGroupSQL, UserSQL

logger = logging.getLogger(__name__)


def get_user_by_email(session: Session, email: str, make_new_user_if_none: bool = True) -> UserSQL:
    """
    Get user by email. If user does not exist, make one.

    :param session: database session
    :param email: email of user
    :param make_new_user_if_none: make user with email if doesn't exist
    :return: user object
    """

    user = session.query(UserSQL).filter(UserSQL.email == email).first()

    if user is None and make_new_user_if_none is True:
        logger.info(f"User with email {email} not found, so making one")

        # checking for site_group
        site_group_name = f"site_group_for_{email}"
        site_group = get_site_group_by_name(session=session, site_group_name=site_group_name)

        # make a new user
        stmt = postgresql.insert(UserSQL.__table__)
        stmt = stmt.on_conflict_do_nothing()
        session.execute(
            stmt, [{"location_group_uuid": site_group.location_group_uuid, "email": email}]
        )

        # get a new user
        user = session.query(UserSQL).filter(UserSQL.email == email).first()

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


def get_site_group_by_name(session: Session, site_group_name: str, create_if_none: bool = True):
    """
    Get site group by name. If site group does not exist, make one.

    :param session: database session
    :param site_group_name: name of site group
    :return: site group object
    """

    site_group = (
        session.query(LocationGroupSQL)
        .filter(LocationGroupSQL.location_group_name == site_group_name)
        .first()
    )

    if (site_group is None) and (create_if_none is True):
        logger.info(f"Site group with name {site_group_name} not found, so making one")

        stmt = postgresql.insert(LocationGroupSQL.__table__)
        stmt = stmt.on_conflict_do_nothing()
        session.execute(stmt, [{"location_group_name": site_group_name}])

        site_group = (
            session.query(LocationGroupSQL)
            .filter(LocationGroupSQL.location_group_name == site_group_name)
            .first()
        )

    return site_group


# get all site groups
def get_all_site_groups(session: Session) -> List[LocationGroupSQL]:
    """
    Get all site groups from the database.

    :param session: database session
    """
    query = session.query(LocationGroupSQL)

    query = query.order_by(LocationGroupSQL.location_group_name.asc())

    site_groups = query.all()

    return site_groups


def get_all_last_api_request(
    session: Session,
    include_in_url: Optional[str] = None,
    exclude_in_url: Optional[str] = None,
) -> List[APIRequestSQL]:
    """
    Get all last api requests for all users.

    :param session: database session
    :return:
    """

    query = session.query(APIRequestSQL)

    if include_in_url is not None:
        query = query.filter(APIRequestSQL.url.like(f"%{include_in_url}%"))

    if exclude_in_url is not None:
        query = query.filter(~APIRequestSQL.url.like(f"%{exclude_in_url}%"))

    last_requests_sql: [APIRequestSQL] = (
        session.query(APIRequestSQL)
        .distinct(APIRequestSQL.user_uuid)
        .join(UserSQL)
        .options(contains_eager(APIRequestSQL.user))
        .populate_existing()
        .order_by(APIRequestSQL.user_uuid, APIRequestSQL.created_utc.desc())
        .all()
    )

    return last_requests_sql


def get_api_requests_for_one_user(
    session: Session,
    email: str,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    include_in_url: Optional[str] = None,
    exclude_in_url: Optional[str] = None,
) -> List[APIRequestSQL]:
    """
    Get all api requests for one user.

    :param session: database session
    :param email: user email
    :param start_datetime: only get api requests after start datetime
    :param end_datetime: only get api requests before end datetime
    """

    query = session.query(APIRequestSQL)
    query = query.join(UserSQL).filter(UserSQL.email == email)

    if include_in_url is not None:
        query = query.filter(APIRequestSQL.url.like(f"%{include_in_url}%"))

    if exclude_in_url is not None:
        query = query.filter(~APIRequestSQL.url.like(f"%{exclude_in_url}%"))

    if start_datetime is not None:
        query = query.filter(APIRequestSQL.created_utc >= start_datetime)

    if end_datetime is not None:
        query = query.filter(APIRequestSQL.created_utc <= end_datetime)

    api_requests: [APIRequestSQL] = query.order_by(APIRequestSQL.created_utc.desc()).all()

    return api_requests
