"""
Functions to read from the Status table
"""

from typing import Optional

from pvsite_datamodel.sqlmodels import StatusSQL
from sqlalchemy.orm import Session


def get_latest_status(session: Session) -> Optional[StatusSQL]:
    """
    Gets the latest entry in the status table. Returns None if there are no entries

    :param session: database session
    return: Latest StatusSQL object, or None
    """

    # Query status table, ordered by created time
    query = session.query(StatusSQL)
    query = query.order_by(StatusSQL.created_utc.desc())

    # get the top result
    latest_status = query.first()

    return latest_status
