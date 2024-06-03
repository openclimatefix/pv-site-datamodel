"""
Functions to read from the database and format.
"""

import logging

from pvsite_datamodel.read.user import get_user_by_email as get_user_by_db
from pvsite_datamodel.sqlmodels import APIRequestSQL

logger = logging.getLogger(__name__)


def save_api_call_to_db(url, session, user=None):
    """
    Save api call to database.
    """
    url = str(url)
    if user is None:
        email = "unknown"
        user = get_user_by_db(session=session, email=email)

    email = user.email

    # make api call
    logger.info(f"Saving api call ({url=}) to database for user {email}")
    api_request = APIRequestSQL(url=url, user=user)

    # commit to database
    session.add(api_request)
    session.commit()
