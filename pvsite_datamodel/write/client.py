"""
Tools for making clients in the database.
"""

import logging
from uuid import UUID

from sqlalchemy.orm.session import Session

from pvsite_datamodel.sqlmodels import ClientSQL, LocationSQL

_log = logging.getLogger(__name__)


def create_client(session: Session, client_name: str) -> ClientSQL:
    """Create a client.

    :param session: database session
    :param client_name: name of client being created
    """
    client = ClientSQL(client_name=client_name)

    session.add(client)
    session.commit()

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


def assign_site_to_client(session: Session, site_uuid: str, client_name: str) -> str:
    """Assign site to client.

    :param session: database session
    :param site_uuid: uuid of site
    :param client_name: name of the client the site will be assigned to.
    """

    client = session.query(ClientSQL).filter(ClientSQL.client_name == client_name).first()

    site = session.query(LocationSQL).filter(LocationSQL.location_uuid == site_uuid).first()

    site.client_uuid = client.client_uuid

    session.add(site)
    session.commit()

    message = (
        f"Site with location uuid {site_uuid} successfully assigned to the client {client_name}"
    )

    return message
