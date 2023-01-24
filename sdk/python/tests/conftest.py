""" Pytest fixtures for tests """

from datetime import datetime, timedelta, timezone
from typing import List

import pytest
import uuid

from pvsite_datamodel.sqlmodels import Base, ClientSQL, SiteSQL, GenerationSQL
from pvsite_datamodel.write.datetime_intervals import get_or_else_create_datetime_interval

from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def session(request):
    postgres = PostgresContainer("postgres:14.5").start()

    # create session with db container information
    engine = create_engine(postgres.get_connection_url())
    version, = engine.execute("select version()").fetchone()

    # create schema in database
    Base.metadata.create_all(engine)

    session = Session(bind=engine)

    def stop_db():
        print("[fixture] stopping db container")
        session.close()
        session.flush()
        postgres.stop()

    request.addfinalizer(stop_db)
    return session


@pytest.fixture()
def sites(session) -> List[SiteSQL]:
    """create some fake sites"""

    sites: List[SiteSQL] = []
    for i in range(0, 4):
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
            ml_id=i,
        )

        session.add(client)
        session.add(site)
        session.commit()

        sites.append(site)

    return sites


@pytest.fixture()
def generations(session, sites):
    """Create some fake generations"""

    start_times = [datetime.today() - timedelta(minutes=x) for x in range(10)]

    all_generations = []
    for site in sites:
        for i in range(0, 10):
            datetime_interval, _ = get_or_else_create_datetime_interval(
                session=session, start_time=start_times[i]
            )

            generation = GenerationSQL(
                generation_uuid=uuid.uuid4(),
                site_uuid=site.site_uuid,
                power_kw=i,
                datetime_interval_uuid=datetime_interval.datetime_interval_uuid,
            )
            all_generations.append(generation)

    session.add_all(all_generations)
    session.commit()


@pytest.fixture()
def test_time():
    return datetime(2022, 7, 25, 0, 0, 0, 0, timezone.utc)


@pytest.fixture()
def forecast_valid_site(sites):
    site_uuid = sites[0].site_uuid

    return {
        "target_datetime_utc": [
            (datetime.today() - timedelta(minutes=x)).isoformat() for x in range(10)
        ],
        "forecast_kw": [float(x) for x in range(10)],
        "pv_uuid": [site_uuid for x in range(10)],
    }


@pytest.fixture()
def forecast_invalid_site():
    return {
        "target_datetime_utc": [datetime.today().isoformat()],
        "forecast_kw": [1.0],
        "pv_uuid": [uuid.uuid4()],
    }


@pytest.fixture()
def generation_valid_site(sites):
    site_uuid = sites[0].site_uuid

    return {
        "start_datetime_utc": [(datetime.today() - timedelta(minutes=x)) for x in range(10)],
        "power_kw": [float(x) for x in range(10)],
        "site_uuid": [site_uuid for x in range(10)],
    }


@pytest.fixture()
def generation_invalid_site():
    return {
        "start_datetime_utc": [datetime.today()],
        "power_kw": [1.0],
        "site_uuid": [uuid.uuid4()],
    }
