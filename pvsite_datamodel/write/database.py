import logging
from pvsite_datamodel.read.user import get_user_by_email as get_user_by_db
from pvsite_datamodel.sqlmodels import APIRequestSQL
logger = logging.getLogger(__name__)
def save_api_call_to_db(url, session, user=None):
    """
    Save api call to database

    If the user does not have an email address, we will save the email as unknown
    :param request:
    :return:
    """

    url = str(url)
    if user is None:
        email = "unknown"
    else:
        email = user.email

    # get user from db
    user = get_user_by_db(session=session, email=email)
    # make api call
    logger.info(f"Saving api call ({url=}) to database for user {email}")
    api_request = APIRequestSQL(url=url, user=user)

    # commit to database
    session.add(api_request)
    session.commit()