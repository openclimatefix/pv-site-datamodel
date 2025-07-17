"""test get models"""

import datetime as dt
from uuid import uuid4

import pandas as pd

from pvsite_datamodel.read.model import get_models, get_or_create_model
from pvsite_datamodel.sqlmodels import MLModelSQL
from pvsite_datamodel.write.forecast import insert_forecast_values


def test_get_model(db_session):
    model_read_1 = get_or_create_model(
        session=db_session,
        name="test_name",
        version="9.9.9",
        description="test_desc",
    )
    model_read_2 = get_or_create_model(session=db_session, name="test_name", version="9.9.9")

    assert model_read_1.name == model_read_2.name
    assert model_read_1.version == model_read_2.version

    assert len(db_session.query(MLModelSQL).all()) == 1

    _ = get_or_create_model(session=db_session, name="test_name", version="9.9.10")
    _ = get_or_create_model(session=db_session, name="test_name", version="9.9.11")
    models = db_session.query(MLModelSQL).all()
    assert len(models) == 3
    assert models[2].version == "9.9.11"
    assert models[2].description == "test_desc"


def test_get_models(db_session):
    _ = get_or_create_model(session=db_session, name="test_name", version="9.9.9")
    _ = get_or_create_model(session=db_session, name="test_name", version="9.9.10")

    models = get_models(session=db_session)

    assert len(models) == 1
    assert models[0].version == "9.9.10"


def test_get_models_with_datetimes(db_session, forecast_valid_input):
    model = get_or_create_model(session=db_session, name="test_name", version="9.9.10")

    forecast_valid_meta_input, forecast_valid_values_input = forecast_valid_input

    df = pd.DataFrame(forecast_valid_values_input)

    insert_forecast_values(
        session=db_session,
        forecast_meta=forecast_valid_meta_input,
        forecast_values_df=df,
        ml_model_name=model.name,
        ml_model_version=model.version,
    )

    now = dt.datetime.now(dt.UTC)
    models = get_models(session=db_session, start_datetime=now)
    assert len(models) == 1

    models = get_models(session=db_session, start_datetime=now + dt.timedelta(days=1))
    assert len(models) == 0


def test_get_models_with_datetimes_with_sites(db_session, forecast_valid_input):
    model = get_or_create_model(session=db_session, name="test_name", version="9.9.10")

    forecast_valid_meta_input, forecast_valid_values_input = forecast_valid_input

    df = pd.DataFrame(forecast_valid_values_input)

    insert_forecast_values(
        session=db_session,
        forecast_meta=forecast_valid_meta_input,
        forecast_values_df=df,
        ml_model_name=model.name,
        ml_model_version=model.version,
    )

    models = get_models(
        session=db_session,
        start_datetime=dt.datetime.now(dt.UTC) - dt.timedelta(minutes=1),
        site_uuid=forecast_valid_meta_input["location_uuid"],
    )
    assert len(models) == 1

    models = get_models(
        session=db_session,
        start_datetime=dt.datetime.now(dt.UTC),
        site_uuid=str(uuid4()),
    )
    assert len(models) == 0
