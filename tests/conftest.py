"""Pytest fixtures for tests."""
import datetime as dt
import uuid
from typing import List

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from pvsite_datamodel import ClientSQL, GenerationSQL, SiteSQL, StatusSQL
from pvsite_datamodel.sqlmodels import Base


@pytest.fixture(scope="session")
def engine():
    """Database engine fixture."""
    with PostgresContainer("postgres:14.5") as postgres:
        # TODO need to setup postgres database with docker
        url = postgres.get_connection_url()
        engine = create_engine(url)
        Base.metadata.create_all(engine)

        yield engine


@pytest.fixture()
def db_session(engine):
    """Return a sqlalchemy session, which tears down everything properly post-test."""
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction

    with Session(bind=connection) as session:
        yield session

        session.close()
        # roll back the broader transaction
        transaction.rollback()
        # put back the connection to the connection pool
        connection.close()
        session.flush()

    engine.dispose()


@pytest.fixture()
def sites(db_session):
    """Create some fake sites."""
    sites = []
    for i in range(0, 4):
        client = ClientSQL(
            client_name=f"testclient_{i}",
            created_utc=dt.datetime.now(dt.timezone.utc),
        )

        db_session.add(client)
        db_session.commit()

        site = SiteSQL(
            client_uuid=client.client_uuid,
            client_site_id=1,
            latitude=51,
            longitude=3,
            capacity_kw=4,
            created_utc=dt.datetime.now(dt.timezone.utc),
            ml_id=i,
        )
        db_session.add(site)
        db_session.commit()

        sites.append(site)

    return sites


@pytest.fixture()
def generations(db_session, sites):
    """Create some fake generations."""
    start_times = [dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=x) for x in range(10)]

    all_generations = []
    for site in sites:
        for i in range(0, 10):
            generation = GenerationSQL(
                site_uuid=site.site_uuid,
                generation_power_kw=i,
                start_utc=start_times[i],
                end_utc=start_times[i] + dt.timedelta(minutes=5),
            )
            all_generations.append(generation)

    db_session.add_all(all_generations)
    db_session.commit()


@pytest.fixture()
def test_time():
    return dt.datetime(2022, 7, 25, 0, 0, 0, 0, dt.timezone.utc)


@pytest.fixture()
def forecast_valid_site(sites):
    site_uuid = sites[0].site_uuid

    start_utc = [dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=x) for x in range(10)]
    end_utc = [d + dt.timedelta(minutes=10) for d in start_utc]

    return {
        "target_start_utc": start_utc,
        "target_end_utc": end_utc,
        "forecast_kw": [float(x) for x in range(10)],
        "site_uuid": [site_uuid for x in range(10)],
    }


@pytest.fixture()
def forecast_invalid_site():
    now = dt.datetime.now(dt.timezone.utc)
    return {
        "target_start_utc": [now],
        "target_end_utc": [now + dt.timedelta(minutes=10)],
        "forecast_kw": [1.0],
        "site_uuid": [uuid.uuid4()],
    }


@pytest.fixture()
def forecast_invalid_dataframe():
    return {
        "target_datetime_utc": [dt.datetime.now(dt.timezone.utc).isoformat()],
        "forecast_Mw": [1.0],
        "site_uuid": ["not a uuid"],
    }


@pytest.fixture()
def generation_valid_site(sites):
    site_uuid = sites[0].site_uuid

    n_rows = 10

    return {
        "start_utc": [
            dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=x) for x in range(n_rows)
        ],
        "power_kw": [float(x) for x in range(n_rows)],
        "site_uuid": [site_uuid for _ in range(n_rows)],
    }


@pytest.fixture()
def generation_invalid_dataframe():
    return {
        "start_utc": [dt.datetime.now(dt.timezone.utc)],
        "power_kw": [1.0],
        "site_uuid": ["ahsjdkri48ggfhdu47fyajs837ghv612"],
    }


@pytest.fixture()
def statuses(db_session) -> List[StatusSQL]:
    """Create some fake statuses."""
    statuses: List[StatusSQL] = []
    for i in range(0, 4):
        status = StatusSQL(
            status="OK",
            message=f"Status {i}",
        )
        db_session.add(status)
        db_session.commit()
        statuses.append(status)

    return statuses
