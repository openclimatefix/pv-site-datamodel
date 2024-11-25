"""Pytest fixtures for tests."""

import datetime as dt
import json
import os.path
import uuid
from pathlib import Path
from typing import List

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from alembic import command
from alembic.config import Config
from pvsite_datamodel import ClientSQL, GenerationSQL, SiteSQL, StatusSQL
from pvsite_datamodel.write.user_and_site import create_site_group, create_user

PROJECT_PATH = Path(__file__).parent.parent.resolve()


@pytest.fixture(scope="session")
def engine():
    """Database engine fixture."""
    with PostgresContainer("postgres:15.5") as postgres:
        # TODO need to setup postgres database with docker
        url = postgres.get_connection_url()
        engine = create_engine(url)

        # run alembic migrations
        ini_path = os.path.join(PROJECT_PATH, "alembic.ini")
        alembic_cfg = Config(file_=ini_path)
        alembic_dir = os.path.join(PROJECT_PATH, "alembic")
        alembic_cfg.set_main_option("script_location", alembic_dir)
        os.environ["DB_URL"] = url
        command.upgrade(alembic_cfg, "head")

        # If you haven't run alembic migration yet, you might want to just run the tests with this
        # from pvsite_datamodel.sqlmodels import Base
        # Base.metadata.create_all(engine)

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
def sites(db_session, client):
    """Create some fake sites."""

    sites = []
    for i in range(0, 4):
        site = SiteSQL(
            client_site_id=1,
            client_site_name=f"test_site_{i}",
            latitude=51,
            longitude=3,
            capacity_kw=4,
            inverter_capacity_kw=4,
            module_capacity_kw=4.3,
            created_utc=dt.datetime.now(dt.timezone.utc),
            ml_id=i,
            dno=json.dumps({"dno_id": str(i), "name": "unknown", "long_name": "unknown"}),
            gsp=json.dumps({"gsp_id": str(i), "name": "unknown"}),
            client_uuid=client.client_uuid,
        )
        db_session.add(site)
        db_session.commit()

        sites.append(site)

    # make sure they are in order
    sites = db_session.query(SiteSQL).order_by(SiteSQL.site_uuid).all()

    return sites


@pytest.fixture()
def make_sites_for_country(db_session):
    """Create some fake sites for specfic country"""

    def _make_sites_for_country(country="uk"):
        sites = []
        for i in range(0, 4):
            site = SiteSQL(
                client_site_id=1,
                client_site_name=f"test_site_{i}",
                latitude=51,
                longitude=3,
                capacity_kw=4,
                inverter_capacity_kw=4,
                module_capacity_kw=4.3,
                created_utc=dt.datetime.now(dt.timezone.utc),
                ml_id=i,
                dno=json.dumps({"dno_id": str(i), "name": "unknown", "long_name": "unknown"}),
                gsp=json.dumps({"gsp_id": str(i), "name": "unknown"}),
                country=country,
            )
            db_session.add(site)
            db_session.commit()

            sites.append(site)

        # make sure they are in order
        sites = db_session.query(SiteSQL).order_by(SiteSQL.site_uuid).all()

        return sites

    return _make_sites_for_country


@pytest.fixture()
def user_with_sites(db_session, sites):
    """Create a user with sites"""

    site_group = create_site_group(db_session=db_session)
    user = create_user(
        session=db_session, email="test_user@gmail.com", site_group_name=site_group.site_group_name
    )

    site_group.sites = sites
    return user


@pytest.fixture()
def generations(db_session, sites):
    """Create some fake generations."""
    now = dt.datetime.now(dt.timezone.utc)
    start_times = [now - dt.timedelta(minutes=x) for x in range(10)]

    all_generations = []
    for site in sites:
        for i in range(0, 10):
            generation = GenerationSQL(
                site_uuid=site.site_uuid,
                generation_power_kw=10 - i,
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
def forecast_valid_meta_input(sites):
    forecast_meta = {
        "site_uuid": sites[0].site_uuid,
        "timestamp_utc": dt.datetime.now(tz=dt.UTC),
        "forecast_version": "0.0.0",
    }

    return forecast_meta


@pytest.fixture()
def forecast_valid_values_input():
    n = 10  # number of forecast values
    step = 15  # in minutes
    init_utc = dt.datetime.now(dt.timezone.utc)
    start_utc = [init_utc + dt.timedelta(minutes=i * step) for i in range(n)]
    end_utc = [d + dt.timedelta(minutes=step) for d in start_utc]
    forecast_power_kw = [i * 10 for i in range(n)]
    horizon_mins = [int((d - init_utc).seconds / 60) for d in start_utc]
    forecast_values = {
        "start_utc": start_utc,
        "end_utc": end_utc,
        "forecast_power_kw": forecast_power_kw,
        "horizon_minutes": horizon_mins,
    }

    return forecast_values


@pytest.fixture()
def forecast_valid_input(forecast_valid_meta_input, forecast_valid_values_input):
    return (forecast_valid_meta_input, forecast_valid_values_input)


@pytest.fixture()
def forecast_with_invalid_meta_input(forecast_valid_meta_input, forecast_valid_values_input):
    forecast_meta = forecast_valid_meta_input
    forecast_meta["site_uuid"] = "not-a-uuid"
    return (forecast_meta, forecast_valid_values_input)


@pytest.fixture()
def forecast_with_invalid_values_input(forecast_valid_meta_input, forecast_valid_values_input):
    forecast_values = forecast_valid_values_input
    forecast_power_kw = forecast_values["forecast_power_kw"]
    del forecast_values["forecast_power_kw"]
    forecast_values["forecast_power_MW"] = forecast_power_kw
    return (forecast_valid_meta_input, forecast_values)


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
def forecast_invalid_meta():
    return {}


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


@pytest.fixture()
def client(db_session):
    """Create a fake client."""
    client = ClientSQL(client_name="client_name_test")
    db_session.add(client)
    db_session.commit()

    return client
