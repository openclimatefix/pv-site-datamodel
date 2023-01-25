"""
Functions to read from the Status table
"""

from pvsite_datamodel.sqlmodels import StatusSQL
from sqlalchemy.orm import Session


def get_latest_status(session: Session) -> StatusSQL:
    """
    Read last input data last updated

    :param session: database session
    return: Latest input data object
    """

    # Query status table, ordered by created time
    query = session.query(StatusSQL)
    query = query.order_by(StatusSQL.created_utc.desc())

    # get the top result
    latest_status = query.first()

    return latest_status
