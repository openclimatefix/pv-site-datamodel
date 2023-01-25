""" Pytest fixtures for tests """
from datetime import datetime, timedelta, timezone

import pytest
import uuid

from pvsite_datamodel.sqlmodels import Base
from pvsite_datamodel import (
    ClientSQL,
    SiteSQL,
    GenerationSQL,
    StatusSQL,
    LatestForecastValueSQL,
    ForecastSQL,
)
from pvsite_datamodel.write.datetime_intervals import get_or_else_create_datetime_interval

from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from typing import List


@pytest.fixture(scope="session")
def engine():
    with PostgresContainer("postgres:14.5") as postgres:
        # TODO need to setup postgres database with docker
        url = postgres.get_connection_url()
        engine = create_engine(url)
        Base.metadata.create_all(engine)

        yield engine


@pytest.fixture(scope="function", autouse=True)
def db_session(engine):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
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
    """create some fake sites"""

    sites = []
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
        db_session.add(client)
        db_session.add(site)
        db_session.commit()

        sites.append(site)

    return sites


@pytest.fixture()
def generations(db_session, sites):
    """Create some fake generations"""

    start_times = [datetime.today() - timedelta(minutes=x) for x in range(10)]

    all_generations = []
    for site in sites:
        for i in range(0, 10):
            datetime_interval, _ = get_or_else_create_datetime_interval(
                session=db_session, start_time=start_times[i]
            )

            generation = GenerationSQL(
                generation_uuid=uuid.uuid4(),
                site_uuid=site.site_uuid,
                power_kw=i,
                datetime_interval_uuid=datetime_interval.datetime_interval_uuid,
            )
            all_generations.append(generation)

    db_session.add_all(all_generations)
    db_session.commit()


@pytest.fixture()
def latestforecastvalues(db_session, sites):
    """Create some fake latest forecast values"""

    latest_forecast_values = []
    forecast_version: str = "0.0.0"
    start_times = [datetime.today() - timedelta(minutes=x) for x in range(10)]

    for site in sites:
        forecast: ForecastSQL = ForecastSQL(
            forecast_uuid=uuid.uuid4(),
            site_uuid=site.site_uuid,
            forecast_version=forecast_version,
        )
        for i in range(0, 10):
            datetime_interval, _ = get_or_else_create_datetime_interval(
                session=db_session, start_time=start_times[i]
            )

            latest_forecast_value: LatestForecastValueSQL = LatestForecastValueSQL(
                latest_forecast_value_uuid=uuid.uuid4(),
                datetime_interval_uuid=datetime_interval.datetime_interval_uuid,
                forecast_generation_kw=i,
                forecast_uuid=forecast.forecast_uuid,
                site_uuid=site.site_uuid,
                forecast_version=forecast_version,
            )

            latest_forecast_values.append(latest_forecast_value)

    db_session.add_all(latest_forecast_values)
    db_session.commit()


@pytest.fixture()
def datetimeintervals(db_session):
    """Create fake datetime intervals"""

    start_times: List[datetime] = [datetime.today() - timedelta(minutes=x) for x in range(10)]

    for time in start_times:
        get_or_else_create_datetime_interval(session=db_session, start_time=time)


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


@pytest.fixture()
def statuses(db_session) -> List[StatusSQL]:
    """Create some fake statuses"""

    statuses: List[StatusSQL] = []
    for i in range(0, 4):
        status = StatusSQL(
            status_uuid=uuid.uuid4(),
            status="OK",
            message=f"Status {i}",
        )
        db_session.add(status)
        db_session.commit()
        statuses.append(status)

    return statuses
