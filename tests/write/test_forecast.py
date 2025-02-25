import datetime
import uuid

import pandas as pd
import pandas.api.types as ptypes
import pytest
from sqlalchemy.exc import SQLAlchemyError

from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL
from pvsite_datamodel.write.forecast import insert_forecast_values


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
