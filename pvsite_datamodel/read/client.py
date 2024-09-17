""" Functions for reading user data from the database. """

import logging

from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import ClientSQL

logger = logging.getLogger(__name__)


def get_client_by_name(
    session: Session, name: str, make_new_client_if_none: bool = True
) -> ClientSQL:
    """
    Get client by name. If client does not exist, make one.

    :param session: database session
    :param name: name of the client
    :param make_new_client_if_none: make client with name if doesn't exist
    :return: client object
    """

    client = session.query(ClientSQL).filter(ClientSQL.client_name == name).first()

    if client is None:
        if make_new_client_if_none is True:
            logger.info(f"Client with name {name} not found, so making one")

            # make a new client
            client = ClientSQL(client_name=name)
            session.add(client)
            session.commit()
        else:
            raise Exception(f"Could not find client with name {name}")

    return client
