"""Test write functions"""

import pandas as pd
import pytest

from pvsite_datamodel.sqlmodels import (
    SiteSQL,
    DatetimeIntervalSQL,
    ForecastSQL,
    ForecastValueSQL,
    GenerationSQL,
)

from pvsite_datamodel import DatabaseConnection
from pvsite_datamodel.write.datetime_intervals import get_or_else_create_datetime_interval
from pvsite_datamodel.write import insert_forecast_values
from pvsite_datamodel.write import insert_generation_values


class TestDatabaseConnection:
    """Tests for the DatabaseConnection class"""

    def test_connection(self, engine, sites):
        dbcon = DatabaseConnection(engine.url, echo=False)
        with dbcon.get_session() as session:
            session.query(SiteSQL).first()


class TestGetOrElseCreateDatetimeInterval:
    """Tests for the get_or_else_create_datetime_interval function"""

    def test_writes_interval_when_not_exists(self, db_session, test_time):
        # Call function with test_time
        datetime_interval, written_rows = get_or_else_create_datetime_interval(
            session=db_session, start_time=test_time
        )
        assert len(written_rows) > 0

        # Check data has been written and exists in table
        query_result = (
            db_session.query(DatetimeIntervalSQL)
            .filter(
                DatetimeIntervalSQL.datetime_interval_uuid
                == datetime_interval.datetime_interval_uuid
            )
            .first()
        )
        assert query_result is not None

    def test_gets_existing_interval_when_exists(self, db_session, test_time):
        _, written_rows = get_or_else_create_datetime_interval(
            session=db_session, start_time=test_time
        )
        _, written_rows_2 = get_or_else_create_datetime_interval(
            session=db_session, start_time=test_time
        )
        assert len(written_rows) > 0
        assert len(written_rows_2) == 0


class TestInsertForecastValues:
    """Tests for the insert_forecast_values function"""

    def test_inserts_values_for_existing_site(self, db_session, forecast_valid_site):
        df = pd.DataFrame(forecast_valid_site)
        written_rows = insert_forecast_values(session=db_session, df_forecast_values=df)

        assert len(written_rows) == 21
        # 10 datetime intervals, 10 forecast values, 1 forecast

        # Check data has been written and exists in table
        written_forecastvalues = db_session.query(ForecastValueSQL).all()
        assert len(written_forecastvalues) == 10
        written_datetimeintervals = db_session.query(DatetimeIntervalSQL).all()
        assert len(written_datetimeintervals) == 10
        written_forecasts = db_session.query(ForecastSQL).all()
        assert len(written_forecasts) == 1

    def test_inserts_values_for_existing_site_and_existing_datetime_intervals(
            self, db_session, forecast_valid_site
    ):
        """
        Tests inserts values successfully without creating redundant datetime intervals
        """

        # Create DataFrame and write to DB
        df = pd.DataFrame(forecast_valid_site)
        # write once and again,
        _ = insert_forecast_values(session=db_session, df_forecast_values=df)
        written_rows = insert_forecast_values(session=db_session, df_forecast_values=df)
        assert len(written_rows) == 11  # 10 forecast values, 1 forecast

        # Check correct data has been written and exists in table
        written_forecastvalues = db_session.query(ForecastValueSQL).all()
        assert len(written_forecastvalues) == 20  # 10 more since previous test

        written_datetimeintervals = db_session.query(DatetimeIntervalSQL).all()
        assert len(written_datetimeintervals) == 10  # Unchanged from previous test

        written_forecasts = db_session.query(ForecastSQL).all()
        assert len(written_forecasts) == 2  # 1 more since previous test

    def test_errors_on_invalid_site(self, db_session, forecast_invalid_site):
        """Tests function errors when incoming pv_uuid does not exist in sites table"""

        df = pd.DataFrame(forecast_invalid_site)
        with pytest.raises(KeyError):
            written_rows = insert_forecast_values(session=db_session, df_forecast_values=df)
            assert len(written_rows), 0


class TestInsertGenerationValues:
    """Tests for the insert_generation_values function"""

    def test_inserts_generation_for_existing_site(self, db_session, generation_valid_site):
        """Tests inserts values successfully"""

        df = pd.DataFrame(generation_valid_site)
        written_rows = insert_generation_values(session=db_session, generation_values_df=df)

        assert len(written_rows) == 20
        # 10 datetime intervals, 10 generation values

        # Check data has been written and exists in table
        written_forecastvalues = db_session.query(GenerationSQL).all()
        assert len(written_forecastvalues) == 10
        written_datetimeintervals = db_session.query(DatetimeIntervalSQL).all()
        assert len(written_datetimeintervals) == 10
