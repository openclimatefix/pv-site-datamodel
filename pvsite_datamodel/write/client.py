"""
Tools for making clients in the database.
"""

import logging
from uuid import UUID

from sqlalchemy.orm.session import Session

from pvsite_datamodel.sqlmodels import ClientSQL

_log = logging.getLogger(__name__)


def create_client(session: Session, client_name: str) -> ClientSQL:
    """Create a client.

    :param session: database session
    :param client_name: name of client being created
    """
    client = ClientSQL(client_name=client_name)

    session.add(client)
    session.commit()
    session.refresh(client)

    return client


def edit_client(session: Session, client_uuid: UUID, client_name: str) -> ClientSQL:
    """Edit an existing client.

    :param session: database session
    :param client_uuid: the existing client uuid
    :param client_name: name of the client
    """
    client = session.query(ClientSQL).filter(ClientSQL.client_uuid == client_uuid).first()

    client.client_name = client_name

    session.add(client)
    session.commit()

    return client
