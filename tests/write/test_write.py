"""Test write functions."""

import datetime
import uuid

import pandas as pd
import pandas.api.types as ptypes
import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from pvsite_datamodel.pydantic_models import PVSiteEditMetadata
from pvsite_datamodel.read.user import get_user_by_email
from pvsite_datamodel.sqlmodels import (
    APIRequestSQL,
    ForecastSQL,
    ForecastValueSQL,
    GenerationSQL,
    SiteHistorySQL,
)
from pvsite_datamodel.write.client import assign_site_to_client, create_client, edit_client
from pvsite_datamodel.write.database import save_api_call_to_db
from pvsite_datamodel.write.forecast import insert_forecast_values
from pvsite_datamodel.write.generation import insert_generation_values
from pvsite_datamodel.write.user_and_site import (
    add_site_to_site_group,
    assign_model_name_to_site,
    change_user_site_group,
    create_site,
    create_site_group,
    create_user,
    edit_site,
    make_fake_site,
)


class TestInsertForecastValues:
    """Tests for the insert_forecast_values function."""

    def test_insert_forecast_for_existing_site(self, db_session, forecast_valid_input):
        """Test if forecast and forecast values inserted successfully"""
        forecast_meta, forecast_values = forecast_valid_input
        forecast_values_df = pd.DataFrame(forecast_values)

        assert "site_uuid" in forecast_meta
        assert "timestamp_utc" in forecast_meta
        assert "forecast_version" in forecast_meta

        assert isinstance(forecast_meta["site_uuid"], uuid.UUID)
        assert isinstance(forecast_meta["timestamp_utc"], datetime.datetime)
        assert isinstance(forecast_meta["forecast_version"], str)

        assert "start_utc" in forecast_values_df.columns
        assert "end_utc" in forecast_values_df.columns
        assert "forecast_power_kw" in forecast_values_df.columns
        assert "horizon_minutes" in forecast_values_df.columns

        assert ptypes.is_datetime64_any_dtype(forecast_values_df["start_utc"])
        assert ptypes.is_datetime64_any_dtype(forecast_values_df["end_utc"])
        assert ptypes.is_numeric_dtype(forecast_values_df["forecast_power_kw"])
        assert ptypes.is_numeric_dtype(forecast_values_df["horizon_minutes"])

        insert_forecast_values(
            db_session,
            forecast_meta,
            forecast_values_df,
            ml_model_name="test",
            ml_model_version="0.0.0",
        )

        assert db_session.query(ForecastSQL).count() == 1
        assert db_session.query(ForecastValueSQL).count() == 10

    def test_invalid_forecast_meta(self, db_session, forecast_with_invalid_meta_input):
        """Test function errors on invalid forecast metadata"""
        forecast_meta, forecast_values = forecast_with_invalid_meta_input
        forecast_values_df = pd.DataFrame(forecast_values)

        with pytest.raises(SQLAlchemyError):
            insert_forecast_values(db_session, forecast_meta, forecast_values_df)

    def test_invalid_forecast_values_dataframe(
        self, db_session, forecast_with_invalid_values_input
    ):
        """test function errors on invalid forecast values dataframe"""
        forecast_meta, forecast_values = forecast_with_invalid_values_input
        forecast_values_df = pd.DataFrame(forecast_values)

        with pytest.raises(
            TypeError,
            match=r"^'forecast_power_MW' is an invalid keyword argument for ForecastValueSQL.*",
        ):
            insert_forecast_values(db_session, forecast_meta, forecast_values_df)


class TestInsertGenerationValues:
    """Tests for the insert_generation_values function."""

    def test_inserts_generation_for_existing_site(self, db_session, generation_valid_site):
        """Tests inserts values successfully."""
        df = pd.DataFrame(generation_valid_site)
        insert_generation_values(db_session, df)
        db_session.commit()
        # Check data has been written and exists in table
        assert db_session.query(GenerationSQL).count() == 10

    def test_errors_on_invalid_dataframe(self, engine, generation_invalid_dataframe):
        """Tests function errors on invalid dataframe."""
        df = pd.DataFrame(generation_invalid_dataframe)

        with Session(bind=engine) as session:
            num_rows = session.query(GenerationSQL).count()

            with session.begin_nested():
                with pytest.raises(SQLAlchemyError):
                    insert_generation_values(session, df)
                session.rollback()

            # Make sure nothing was written
            assert session.query(GenerationSQL).count() == num_rows

    def test_inserts_generation_duplicates(self, db_session, generation_valid_site):
        """Tests no duplicates."""
        df = pd.DataFrame(generation_valid_site)
        insert_generation_values(db_session, df)
        db_session.commit()
        # Check data has been written and exists in table
        assert db_session.query(GenerationSQL).count() == 10

        # insert the same values
        insert_generation_values(db_session, df)
        db_session.commit()
        assert db_session.query(GenerationSQL).count() == 10


# create new site, this will be one in a different issue
def test_create_new_site(db_session):
    site, message = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_name",
        latitude=51.0,
        longitude=0.0,
        capacity_kw=1.0,
    )

    assert site.client_site_name == "test_site_name"
    assert site.ml_id == 1
    assert site.client_site_id == 6932
    assert site.country == "uk"
    assert (
        message == f"Site with client site id {site.client_site_id} "
        f"and site uuid {site.site_uuid} created successfully"
    )


def test_create_new_site_with_user(db_session):
    user = get_user_by_email(session=db_session, email="test@test.com")

    site, message = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_1",
        latitude=51.0,
        longitude=0.0,
        capacity_kw=1.0,
        user_uuid=user.user_uuid,
    )

    # after creating there should be an entry in the history table
    h_site = (
        db_session.query(SiteHistorySQL).filter(SiteHistorySQL.operation_type == "INSERT").first()
    )

    assert h_site.site_uuid == site.site_uuid
    assert h_site.changed_by == user.user_uuid

    # create site without setting user
    site_2, _ = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_2",
        latitude=51.0,
        longitude=0.0,
        capacity_kw=1.0,
    )

    h_site_2 = (
        db_session.query(SiteHistorySQL)
        .filter(SiteHistorySQL.site_uuid == site_2.site_uuid)
        .first()
    )

    # user should not be set
    assert h_site_2.changed_by is None


def test_create_new_site_in_specified_country(db_session):
    site, message = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_name",
        latitude=51.0,
        longitude=0.0,
        capacity_kw=1.0,
        country="india",
    )

    assert site.country == "india"
    assert (
        message == f"Site with client site id {site.client_site_id} "
        f"and site uuid {site.site_uuid} created successfully"
    )


def test_create_new_site_with_invalid_asset_type(db_session):
    with pytest.raises(ValueError, match=r"^Invalid asset_type.*"):
        site, message = create_site(
            session=db_session,
            client_site_id=6932,
            client_site_name="test_site_name",
            latitude=51.0,
            longitude=0.0,
            capacity_kw=1.0,
            asset_type="invalid-asset",
        )


# test for create_new_site to check ml_id increments
def test_create_new_site_twice(db_session):
    """Test create new site function for ml_id"""

    site_1, _ = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_name",
        latitude=1.0,
        longitude=1.0,
        capacity_kw=1.0,
    )

    site_2, _ = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_name",
        latitude=1.0,
        longitude=1.0,
        capacity_kw=1.0,
    )

    assert site_1.ml_id == 1
    assert site_2.ml_id == 2


# test for create_site to check ml_id duplicates are allowed for separate clients
def test_ml_id_duplicate_for_unique_clients(db_session):
    """Test create sites with duplicate ml_id for different clients"""

    site_1, _ = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_name_1",
        latitude=1.0,
        longitude=1.0,
        capacity_kw=1.0,
        ml_id=1,
    )

    site_2, _ = create_site(
        session=db_session,
        client_site_id=6933,
        client_site_name="test_site_name_2",
        latitude=1.0,
        longitude=1.0,
        capacity_kw=1.0,
        ml_id=1,
    )

    assert site_1.ml_id == 1
    assert site_2.ml_id == 1


def test_create_user(db_session):
    "Test to create a new user."

    site_group_1 = create_site_group(db_session=db_session)

    user_1 = create_user(
        session=db_session,
        email="test_user@test.org",
        site_group_name=site_group_1.site_group_name,
    )

    assert user_1.email == "test_user@test.org"
    assert user_1.site_group.site_group_name == "test_site_group"
    assert user_1.site_group_uuid == site_group_1.site_group_uuid


# add site to site group
def test_add_site_to_site_group(db_session):
    site_group = create_site_group(db_session=db_session)
    site_1 = make_fake_site(db_session=db_session, ml_id=1)
    site_2 = make_fake_site(db_session=db_session, ml_id=2)
    site_3 = make_fake_site(db_session=db_session, ml_id=3)
    site_group.sites.append(site_1)
    site_group.sites.append(site_2)

    add_site_to_site_group(
        session=db_session,
        site_uuid=str(site_3.site_uuid),
        site_group_name=site_group.site_group_name,
    )

    assert len(site_group.sites) == 3


# test change user site group
def test_change_user_site_group(db_session):
    """Test the change user site group function
    :param db_session: the database session"""
    site_group = create_site_group(db_session=db_session)
    user = create_user(
        session=db_session, email="test_user@gmail.com", site_group_name=site_group.site_group_name
    )
    site_group2 = create_site_group(db_session=db_session, site_group_name="test_site_group2")
    user, user_site_group = change_user_site_group(
        session=db_session,
        email="test_user@gmail.com",
        site_group_name=site_group2.site_group_name,
    )

    assert user_site_group == site_group2.site_group_name
    assert user == "test_user@gmail.com"


def test_save_api_call_to_db(db_session):
    user = get_user_by_email(session=db_session, email="test@test.com")
    url = "test"
    save_api_call_to_db(url=url, session=db_session, user=user)
    assert len(db_session.query(APIRequestSQL).all()) == 1


def test_edit_site(db_session):
    """Test the update of site metadata"""
    # history table should be empty
    hist_size = db_session.query(SiteHistorySQL).count()
    assert hist_size == 0

    site = make_fake_site(db_session=db_session)

    # history table should contain a single entry
    hist_size = db_session.query(SiteHistorySQL).count()
    assert hist_size == 1

    prev_latitude = site.latitude

    metadata_to_update = PVSiteEditMetadata(tilt=15, capacity_kw=None)

    user = get_user_by_email(session=db_session, email="test@test.com")
    site, _ = edit_site(
        session=db_session,
        site_uuid=str(site.site_uuid),
        site_info=metadata_to_update,
        user_uuid=user.user_uuid,
    )

    assert site.tilt == metadata_to_update.tilt
    assert site.capacity_kw == metadata_to_update.capacity_kw
    assert site.latitude == prev_latitude

    # after editing there should be another entry in the history table
    h_site = (
        db_session.query(SiteHistorySQL).filter(SiteHistorySQL.operation_type == "UPDATE").first()
    )

    assert h_site.site_uuid == site.site_uuid
    assert h_site.changed_by == user.user_uuid


def test_create_client(db_session):
    """Test to create a new client"""
    client = create_client(session=db_session, client_name="Test Client")

    assert client.client_name == "Test Client"


def test_edit_client(db_session):
    """Test to edit a client"""
    client = create_client(session=db_session, client_name="Test Client")

    client = edit_client(
        session=db_session,
        client_uuid=client.client_uuid,
        client_name="Edited Client",
    )

    assert client.client_name == "Edited Client"


def test_assign_site_to_client(db_session):
    """Test to assign a site to a client"""
    site = make_fake_site(db_session=db_session)
    client = create_client(session=db_session, client_name="Test Client")

    message = assign_site_to_client(db_session, site.site_uuid, client.client_name)

    assert site.client_uuid == client.client_uuid
    assert message == (
        f"Site with site uuid {site.site_uuid} successfully assigned "
        f"to the client {client.client_name}"
    )


def test_assign_model_name_to_site(db_session):
    """Test to assign a model name to a site"""
    site = make_fake_site(db_session=db_session)

    assign_model_name_to_site(db_session, site.site_uuid, "test_model")

    assert site.ml_model.name == "test_model"

    assign_model_name_to_site(db_session, site.site_uuid, "test_model_2")

    assert site.ml_model.name == "test_model_2"


def test_assign_model_to_nonexistent_site(db_session):
    """Test assigning a model to a nonexistent site"""
    nonexistent_site_uuid = str(uuid.uuid4())

    with pytest.raises(
        KeyError, match=f"Site uuid {nonexistent_site_uuid} not found in sites table"
    ):
        assign_model_name_to_site(db_session, nonexistent_site_uuid, "test_model")
