"""Tests for forecast curtailment integration."""
import datetime as dt
from pvsite_datamodel.read.latest_forecast_values import get_latest_forecast_values_by_site
from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL, CurtailmentSQL

def test_forecast_with_curtailment(db_session, test_site):
    """Test forecast values are reduced during curtailment periods."""
    # Create test forecast
    forecast = ForecastSQL(
        site_uuid=test_site.site_uuid,
        timestamp_utc=dt.datetime.utcnow(),
        forecast_version="test"
    )
    db_session.add(forecast)
    
    # Create forecast values
    start_time = dt.datetime(2023, 1, 1, 12, 0)
    for i in range(24):
        fv = ForecastValueSQL(
            forecast_uuid=forecast.forecast_uuid,
            start_utc=start_time + dt.timedelta(hours=i),
            forecast_power_kw=100.0
        )
        db_session.add(fv)
    db_session.commit()

    # Create curtailment for 2pm-4pm
    curtailment = CurtailmentSQL(
        site_uuid=test_site.site_uuid,
        from_date=dt.date(2023, 1, 1),
        to_date=dt.date(2023, 1, 1),
        from_time_utc=dt.time(14, 0),
        to_time_utc=dt.time(16, 0),
        curtailment_kw=50.0
    )
    db_session.add(curtailment)
    db_session.commit()

    # Get forecasts with curtailment applied
    forecasts = get_latest_forecast_values_by_site(
        db_session,
        site_uuids=[test_site.site_uuid],
        start_utc=dt.datetime(2023, 1, 1, 12, 0),
        apply_curtailments=True
    )

    # Verify curtailment was applied correctly
    forecast_values = forecasts[test_site.site_uuid]
    for fv in forecast_values:
        if dt.time(14, 0) <= fv.start_utc.time() <= dt.time(16, 0):
            assert fv.forecast_power_kw == 50.0  # 100 - 50 curtailment
        else:
            assert fv.forecast_power_kw == 100.0

def test_forecast_without_curtailment(db_session, test_site):
    """Test forecast values remain unchanged when curtailments are disabled."""
    # Create test forecast
    forecast = ForecastSQL(
        site_uuid=test_site.site_uuid,
        timestamp_utc=dt.datetime.utcnow(),
        forecast_version="test"
    )
    db_session.add(forecast)
    
    # Create forecast values
    start_time = dt.datetime(2023, 1, 1, 12, 0)
    for i in range(24):
        fv = ForecastValueSQL(
            forecast_uuid=forecast.forecast_uuid,
            start_utc=start_time + dt.timedelta(hours=i),
            forecast_power_kw=100.0
        )
        db_session.add(fv)
    db_session.commit()

    # Get forecasts without curtailment applied
    forecasts = get_latest_forecast_values_by_site(
        db_session,
        site_uuids=[test_site.site_uuid],
        start_utc=dt.datetime(2023, 1, 1, 12, 0),
        apply_curtailments=False
    )

    # Verify all forecasts remain at original value
    forecast_values = forecasts[test_site.site_uuid]
    for fv in forecast_values:
        assert fv.forecast_power_kw == 100.0
