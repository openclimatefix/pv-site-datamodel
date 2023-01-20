""" Pytest fixtures for tests """
import os

from datetime import datetime, timezone

import pytest
import uuid
from pvsite_datamodel.connection import DatabaseConnection
from pvsite_datamodel.sqlmodels import Base, ClientSQL, SiteSQL


@pytest.fixture
def db_connection():
    """Pytest fixture for a database connection"""

    # TODO need to setup postgres datbase with docker
    url = os.environ["DB_URL"]
    connection = DatabaseConnection(url=url)
    Base.metadata.create_all(connection.engine)

    yield connection

    Base.metadata.drop_all(connection.engine)


@pytest.fixture(scope="function", autouse=True)
def db_session(db_connection):
    """Creates a new database session for a test."""

    connection = db_connection.engine.connect()
    t = connection.begin()

    with db_connection.get_session() as s:
        s.begin()
        yield s

        s.rollback()

        t.rollback()
        connection.close()


@pytest.fixture()
def sites(db_session):
    """ create some fake sites """

    for i in range(0,4):
        client = ClientSQL(
            client_uuid=uuid.uuid4(),
            client_name=f"testclient_{i}",
            created_utc=datetime.now(timezone.utc),
        )
        site = SiteSQL(
            site_uuid=uuid.uuid4(),
            client_uuid=client.client_uuid,
            client_site_id=1,
            latitude=51,
            longitude=3,
            capacity_kw=4,
            created_utc=datetime.now(timezone.utc),
            updated_utc=datetime.now(timezone.utc),
            ml_id=1,
        )
        db_session.add(client)
        db_session.add(site)
        db_session.commit()

