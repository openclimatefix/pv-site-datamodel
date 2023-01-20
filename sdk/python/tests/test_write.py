"""
Tests
"""

import uuid

import pandas as pd
import pytest

from pvsite_datamodel import connection
from pvsite_datamodel import sqlmodels
from pvsite_datamodel.write.datetime_intervals import get_or_else_create_datetime_interval
from pvsite_datamodel.write.forecast import insert_forecast_values
from pvsite_datamodel.write.generation import insert_generation_values

client_uuid = uuid.uuid4()
site_uuid = uuid.uuid4()


def test_connection(engine, sites):

    dbcon = connection.DatabaseConnection(engine.url, echo=False)
    with dbcon.get_session() as session:
        session.query(sqlmodels.SiteSQL).first()


#
def test1_writes_interval_when_not_exist(db_session, test_time):
    """
    Tests that the function writes to the db when the datetime_interval doesn't already exist.

    Needs to be run after test1 to work.
    """
    datetime_interval, written_rows = get_or_else_create_datetime_interval(
        session=db_session, start_time=test_time
    )
    assert len(written_rows) > 0

    # Check data has been written and exists in table
    query_result = (
        db_session.query(sqlmodels.DatetimeIntervalSQL)
        .filter(
            sqlmodels.DatetimeIntervalSQL.datetime_interval_uuid
            == datetime_interval.datetime_interval_uuid
        )
        .first()
    )
    assert query_result is not None


def test_gets_existing_interval_when_exists(db_session, test_time):
    """Tests function doesn't write to db when the datetime_interval already exists"""
    _, written_rows = get_or_else_create_datetime_interval(
        session=db_session, start_time=test_time
    )
    _, written_rows_2 = get_or_else_create_datetime_interval(
        session=db_session, start_time=test_time
    )
    assert len(written_rows) > 0
    assert len(written_rows_2) == 0


def test_inserts_values_for_existing_site(db_session, forecast_valid_site):
    """Tests inserts values successfully"""

    df = pd.DataFrame(forecast_valid_site)
    written_rows = insert_forecast_values(session=db_session, df_forecast_values=df)

    assert len(written_rows) == 21
    # 10 datetime intervals, 10 forecast values, 1 forecast

    # Check data has been written and exists in table
    written_forecastvalues = db_session.query(sqlmodels.ForecastValueSQL).all()
    assert len(written_forecastvalues) == 10
    written_datetimeintervals = db_session.query(sqlmodels.DatetimeIntervalSQL).all()
    assert len(written_datetimeintervals) == 10
    written_forecasts = db_session.query(sqlmodels.ForecastSQL).all()
    assert len(written_forecasts) == 1


def test_inserts_values_for_existing_site_and_existing_datetime_intervals(
    db_session, forecast_valid_site
):
    """
    Tests inserts values successfully without creating redundant datetime intervals

    Needs to be run after test1 to work.
    """

    # Create DataFrame and write to DB
    df = pd.DataFrame(forecast_valid_site)
    # write once and again,
    _ = insert_forecast_values(session=db_session, df_forecast_values=df)
    written_rows = insert_forecast_values(session=db_session, df_forecast_values=df)
    assert len(written_rows) == 11  # 10 forecast values, 1 forecast

    # Check correct data has been written and exists in table
    written_forecastvalues = db_session.query(sqlmodels.ForecastValueSQL).all()
    assert len(written_forecastvalues) == 20  # 10 more since previous test

    written_datetimeintervals = db_session.query(sqlmodels.DatetimeIntervalSQL).all()
    assert len(written_datetimeintervals) == 10  # Unchanged from previous test

    written_forecasts = db_session.query(sqlmodels.ForecastSQL).all()
    assert len(written_forecasts) == 2  # 1 more since previous test


def test_errors_on_invalid_site(db_session, forecast_invalid_site):
    """Tests function errors when incoming pv_uuid does not exist in sites table"""

    df = pd.DataFrame(forecast_invalid_site)
    with pytest.raises(KeyError):
        written_rows = insert_forecast_values(session=db_session, df_forecast_values=df)
        assert len(written_rows), 0


def test_inserts_generation_for_existing_site(db_session, generation_valid_site):
    """Tests inserts values successfully"""

    df = pd.DataFrame(generation_valid_site)
    written_rows = insert_generation_values(session=db_session, generation_values_df=df)

    assert len(written_rows) == 20
    # 10 datetime intervals, 10 generation values

    # Check data has been written and exists in table
    written_forecastvalues = db_session.query(sqlmodels.GenerationSQL).all()
    assert len(written_forecastvalues) == 10
    written_datetimeintervals = db_session.query(sqlmodels.DatetimeIntervalSQL).all()
    assert len(written_datetimeintervals) == 10
