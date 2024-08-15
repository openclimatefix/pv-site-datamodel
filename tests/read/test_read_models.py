""" test get models"""
import pandas as pd

from pvsite_datamodel.read.model import get_models, get_or_create_model
from pvsite_datamodel.sqlmodels import MLModelSQL
from pvsite_datamodel.write.forecast import insert_forecast_values


def test_get_model(db_session):
    model_read_1 = get_or_create_model(session=db_session, name="test_name", version="9.9.9")
    model_read_2 = get_or_create_model(session=db_session, name="test_name", version="9.9.9")

    assert model_read_1.name == model_read_2.name
    assert model_read_1.version == model_read_2.version

    assert len(db_session.query(MLModelSQL).all()) == 1

    _ = get_or_create_model(session=db_session, name="test_name", version="9.9.10")
    assert len(db_session.query(MLModelSQL).all()) == 2


def test_get_models(db_session):
    _ = get_or_create_model(session=db_session, name="test_name", version="9.9.9")
    _ = get_or_create_model(session=db_session, name="test_name", version="9.9.10")

    models = get_models(session=db_session)

    assert len(models) == 1


def test_get_models_with_datetimes(db_session):
    model = get_or_create_model(session=db_session, name="test_name", version="9.9.10")

    df = pd.DataFrame(
        {
            "site_uuid": ["test_uuid"],
            "start_utc": [pd.Timestamp("2021-01-01 00:00:00")],
            "power_kw": [0.0],
        }
    )
    forecast_meta = {
        "site_uuid": "test_uuid",
        "timestamp_utc": pd.Timestamp("2021-01-01 00:00:00"),
        "forecast_version": "0.0.0",
    }

    insert_forecast_values(
        session=db_session,
        forecast_meta=forecast_meta,
        forecast_values_df=df,
        ml_model_name=model.name,
        ml_model_version=model.version,
    )

    _ = get_models(session=db_session, start_datetime=pd.Timestamp("2021-01-01 00:00:00"))
