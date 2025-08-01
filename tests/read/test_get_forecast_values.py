import datetime as dt


from pvsite_datamodel import ForecastSQL, ForecastValueSQL, LocationSQL

from pvsite_datamodel.read import (
    get_forecast_values_fast,
    get_or_create_model,
    get_forecast_values_day_ahead_fast,
)


def _add_fv(
    session,
    forecast,
    power: int,
    ts,
    horizon_minutes: int | None = None,
    created_utc: dt.datetime | None = None,
    model_name: str | None = None,
    probabilistic_values: dict | None = None,
):
    fv = ForecastValueSQL(
        forecast_uuid=forecast.forecast_uuid,
        forecast_power_kw=power,
        start_utc=ts,
        end_utc=ts + dt.timedelta(minutes=5),
        probabilistic_values=probabilistic_values if probabilistic_values is not None else {},
    )
    if horizon_minutes:
        fv.horizon_minutes = horizon_minutes

    if created_utc:
        fv.created_utc = created_utc

    if model_name is not None:
        model = get_or_create_model(session, model_name)
        fv.ml_model_uuid = str(model.model_uuid)

    session.add(fv)


def test_get_forecast_values(db_session, sites):
    site_uuids = [
        site.location_uuid for site in db_session.query(LocationSQL.location_uuid).limit(2)
    ]

    s1, s2 = site_uuids

    forecast_version = "123"

    # Make sure we have some forecasts in the DB
    s1_f1 = ForecastSQL(
        location_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )
    s1_f2 = ForecastSQL(
        location_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1, 0, 10),
    )
    s2_f1 = ForecastSQL(
        location_uuid=s2,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )

    db_session.add_all([s1_f1, s1_f2, s2_f1])
    db_session.commit()

    d0 = dt.datetime(2000, 1, 1, 0, tzinfo=dt.UTC)
    d1 = dt.datetime(2000, 1, 1, 1, tzinfo=dt.UTC)
    d2 = dt.datetime(2000, 1, 1, 2, tzinfo=dt.UTC)
    d3 = dt.datetime(2000, 1, 1, 3, tzinfo=dt.UTC)
    d4 = dt.datetime(2000, 1, 1, 4, tzinfo=dt.UTC)

    # site 1 forecast 1
    _add_fv(db_session, s1_f1, 1.0, d0, horizon_minutes=0)
    _add_fv(db_session, s1_f1, 2.0, d1, horizon_minutes=60)
    _add_fv(db_session, s1_f1, 3.0, d2, horizon_minutes=120)

    # site 1 forecast 2
    _add_fv(db_session, s1_f2, 4.0, d2, horizon_minutes=60)
    _add_fv(db_session, s1_f2, 5.0, d3, horizon_minutes=120)
    _add_fv(db_session, s1_f2, 6.0, d4, horizon_minutes=180)

    # Site 2 forecast 1
    _add_fv(db_session, s2_f1, 7.0, d0, horizon_minutes=0)
    _add_fv(db_session, s2_f1, 8.0, d1, horizon_minutes=60)
    _add_fv(db_session, s2_f1, 9.0, d2, horizon_minutes=120)
    db_session.commit()

    forecast_value = get_forecast_values_fast(db_session, site_uuids[0], d1)

    expected = [(d1, 2), (d2, 4), (d3, 5), (d4, 6)]

    assert len(forecast_value) == 4

    # loop over values in forecast_values and expected
    for i, fv in enumerate(forecast_value):
        assert fv.start_utc == expected[i][0].replace(tzinfo=None)
        assert fv.forecast_power_kw == expected[i][1]


def test_get_forecast_values_with_end_utc(db_session, sites):
    # ****** setup ******
    site_uuids = [
        site.location_uuid for site in db_session.query(LocationSQL.location_uuid).limit(2)
    ]

    s1, s2 = site_uuids

    forecast_version = "123"

    # Make sure we have some forecasts in the DB
    s1_f1 = ForecastSQL(
        location_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )
    s1_f2 = ForecastSQL(
        location_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1, 0, 10),
    )
    s2_f1 = ForecastSQL(
        location_uuid=s2,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )

    db_session.add_all([s1_f1, s1_f2, s2_f1])
    db_session.commit()

    d0 = dt.datetime(2000, 1, 1, 0, tzinfo=dt.UTC)
    d1 = dt.datetime(2000, 1, 1, 1, tzinfo=dt.UTC)
    d2 = dt.datetime(2000, 1, 1, 2, tzinfo=dt.UTC)
    d3 = dt.datetime(2000, 1, 1, 3, tzinfo=dt.UTC)
    d4 = dt.datetime(2000, 1, 1, 4, tzinfo=dt.UTC)

    # site 1 forecast 1
    _add_fv(db_session, s1_f1, 1.0, d0, horizon_minutes=0)
    _add_fv(db_session, s1_f1, 2.0, d1, horizon_minutes=60)
    _add_fv(db_session, s1_f1, 3.0, d2, horizon_minutes=120)

    # site 1 forecast 2
    _add_fv(db_session, s1_f2, 4.0, d2, horizon_minutes=60)
    _add_fv(db_session, s1_f2, 5.0, d3, horizon_minutes=120)
    _add_fv(db_session, s1_f2, 6.0, d4, horizon_minutes=180)

    # Site 2 forecast 1
    _add_fv(db_session, s2_f1, 7.0, d0, horizon_minutes=0)
    _add_fv(db_session, s2_f1, 8.0, d1, horizon_minutes=60)
    _add_fv(db_session, s2_f1, 9.0, d2, horizon_minutes=120)
    db_session.commit()

    # ****** setup ******

    forecast_value = get_forecast_values_fast(db_session, site_uuids[0], d1, end_utc=d2)

    expected = [(d1.replace(tzinfo=None), 2)]
    assert len(forecast_value) == 1

    for i, fv in enumerate(forecast_value):
        assert fv.start_utc == expected[i][0].replace(tzinfo=None)
        assert fv.forecast_power_kw == expected[i][1]


def test_get_forecast_values_day_head(db_session, sites):
    """Test to get DA forecasts"""
    site_uuids = [
        site.location_uuid for site in db_session.query(LocationSQL.location_uuid).limit(2)
    ]

    s1, s2 = site_uuids

    forecast_version = "123"

    cr0 = dt.datetime(2000, 1, 1, 0)
    cr1 = dt.datetime(2000, 1, 2, 0)
    # this is past 9 o'clock so not loaded when looking at da
    cr2 = dt.datetime(2000, 1, 2, 10)

    # Make sure we have some forecasts in the DB
    s1_f0 = ForecastSQL(
        location_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=cr0,
        created_utc=cr0
    )
    s1_f1 = ForecastSQL(
        location_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=cr1,
        created_utc=cr1
    )
    s1_f2 = ForecastSQL(
        location_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=cr2,
        created_utc=cr2
    )

    db_session.add_all([s1_f0, s1_f1, s1_f2])
    db_session.commit()

    d1 = cr1
    d2 = cr1 + dt.timedelta(hours=24)
    d3 = cr1 + dt.timedelta(hours=25)
    d4 = cr1 + dt.timedelta(hours=26)

    # site 1 forecast 0, made at 2000-01-01
    # this should not be loaded as a DA forecast
    _add_fv(db_session, s1_f0, 0.0, cr0, horizon_minutes=15, created_utc=cr0, model_name="test1")
    # this should be loaded as a DA forecast
    _add_fv(db_session, s1_f0, 0.0, d1, horizon_minutes=1440, created_utc=cr0, model_name="test1")

    # site 1 forecast 1, made at 2000-01-02
    # this should not be loaded as a DA forecast
    _add_fv(db_session, s1_f1, 0.1, cr1, horizon_minutes=15, created_utc=cr1, model_name="test1")
    # these should be loaded as a DA forecast
    _add_fv(db_session, s1_f1, 1.0, d2, horizon_minutes=1440, created_utc=cr1, model_name="test1")
    _add_fv(db_session, s1_f1, 2.0, d3, horizon_minutes=1500, created_utc=cr1, model_name="test1")
    _add_fv(db_session, s1_f1, 3.0, d4, horizon_minutes=1560, created_utc=cr1, model_name="test1")

    # site 1 forecast 2, made at 2000-01-02 10:00
    # these should not be loaded as a DA forecast
    _add_fv(db_session, s1_f1, 0.2, cr2, horizon_minutes=15, created_utc=cr2, model_name="test1")
    _add_fv(db_session, s1_f2, 4.0, d2, horizon_minutes=840, created_utc=cr2, model_name="test1")
    _add_fv(db_session, s1_f2, 5.0, d3, horizon_minutes=900, created_utc=cr2, model_name="test1")
    _add_fv(db_session, s1_f2, 6.0, d4, horizon_minutes=960, created_utc=cr2, model_name="test1")

    forecast_values = get_forecast_values_day_ahead_fast(
        session=db_session,
        site_uuid=site_uuids[0],
        start_utc=d1,
        day_ahead_hours=9,
        model_name="test1"
    )

    expected = [(d1, 0), (d2, 1), (d3, 2), (d4, 3)]
    assert len(forecast_values) == len(expected)

    for i, fv in enumerate(forecast_values):
        assert fv.start_utc == expected[i][0].replace(tzinfo=None)
        assert fv.forecast_power_kw == expected[i][1]


def test_get_latest_forecast_values_day_head_with_timezone(db_session, sites):
    """Test to get DA forecasts in a different timezone"""
    site_uuids = [
        site.location_uuid for site in db_session.query(LocationSQL.location_uuid).limit(2)
    ]

    s1, s2 = site_uuids

    forecast_version = "123"

    # Make sure we have some forecasts in the DB
    s1_f1 = ForecastSQL(
        location_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )
    s1_f2 = ForecastSQL(
        location_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1, 0, 10),
    )

    db_session.add_all([s1_f1, s1_f2])
    db_session.commit()

    d0 = dt.datetime(2000, 1, 2, 19)
    d1 = dt.datetime(2000, 1, 2, 20)
    d2 = dt.datetime(2000, 1, 2, 21)
    cr1 = dt.datetime(2000, 1, 1, 0)
    cr2 = dt.datetime(2000, 1, 2, 0)

    # site 1 forecast 1
    _add_fv(db_session, s1_f1, 1.0, d0, created_utc=cr1)
    _add_fv(db_session, s1_f1, 2.0, d1, created_utc=cr1)
    _add_fv(db_session, s1_f1, 3.0, d2, created_utc=cr1)

    # site 1 forecast 2
    _add_fv(db_session, s1_f2, 4.0, d0, created_utc=cr2)
    _add_fv(db_session, s1_f2, 5.0, d1, created_utc=cr2)
    _add_fv(db_session, s1_f2, 6.0, d2, created_utc=cr2)

    forecast_values = get_forecast_values_day_ahead_fast(
        session=db_session,
        site_uuid=site_uuids[0],
        start_utc=d0,
        day_ahead_hours=9,
        day_ahead_timezone_delta_hours=4.5,
    )

    expected = [(d0, 1), (d1, 5), (d2, 6)]

    for i, fv in enumerate(forecast_values):
        assert fv.start_utc == expected[i][0].replace(tzinfo=None)
        assert fv.forecast_power_kw == expected[i][1]


def test_get_latest_forecast_values_model_name(db_session, sites):
    site_uuids = [
        site.location_uuid for site in db_session.query(LocationSQL.location_uuid).limit(2)
    ]

    s1, s2 = site_uuids

    # Make sure we have some forecasts in the DB
    s1_f1 = ForecastSQL(
        location_uuid=s1,
        forecast_version="123",
        timestamp_utc=dt.datetime(2000, 1, 1),
    )

    db_session.add_all([s1_f1])
    db_session.commit()

    d0 = dt.datetime(2000, 1, 1, 0, tzinfo=dt.UTC)
    d1 = dt.datetime(2000, 1, 1, 1, tzinfo=dt.UTC)
    d2 = dt.datetime(2000, 1, 1, 2, tzinfo=dt.UTC)

    # site 1 forecast 1
    _add_fv(db_session, s1_f1, 1.0, d0, horizon_minutes=0, model_name="test_1")
    _add_fv(db_session, s1_f1, 2.0, d1, horizon_minutes=60, model_name="test_1")
    _add_fv(db_session, s1_f1, 3.0, d2, horizon_minutes=120, model_name="test_2")
    db_session.commit()

    forecast_values = get_forecast_values_fast(
        session=db_session,
        site_uuid=site_uuids[0],
        start_utc=d0,
    )
    assert len(forecast_values) == 3

    forecast_values = get_forecast_values_fast(
        session=db_session,
        site_uuid=site_uuids[0],
        start_utc=d0,
        model_name="test_1",
    )
    assert len(forecast_values) == 2

    forecast_values = get_forecast_values_fast(
        session=db_session,
        site_uuid=site_uuids[0],
        start_utc=d0,
        model_name="test_x",
    )
    assert len(forecast_values) == 0


def test_get_latest_forecast_values_probabilistic_value_limit2(db_session, sites):
    # Retrieve two sites for testing (limit(2))
    site_uuids = [
        site.location_uuid for site in db_session.query(LocationSQL.location_uuid).limit(2)
    ]
    site1, site2 = site_uuids

    forecast_version = "123"

    # Create a forecast for each site
    forecast1 = ForecastSQL(
        location_uuid=site1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )
    forecast2 = ForecastSQL(
        location_uuid=site2,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )
    db_session.add_all([forecast1, forecast2])
    db_session.commit()

    d0 = dt.datetime(2000, 1, 1, 0, tzinfo=dt.UTC)

    # For site1: Add a forecast value with explicit probabilistic_values provided
    prob_values = {"p10": 10, "p50": 50, "p90": 90}
    _add_fv(
        db_session,
        forecast1,
        power=1.0,
        ts=d0,
        horizon_minutes=0,
        probabilistic_values=prob_values,
    )

    # For site2: Add a forecast value without providing probabilistic_values (defaults to {})
    _add_fv(
        db_session,
        forecast2,
        power=2.0,
        ts=d0,
        horizon_minutes=0,
    )

    db_session.commit()

    # Retrieve the latest forecast values starting from d0 for both sites
    forecast_values = get_forecast_values_fast(db_session, site_uuids[0], d0)

    # Expect one forecast value for each site
    assert len(forecast_values) == 1

    # Retrieve the forecast values for each site
    fv_site1 = forecast_values[0]

    # Assert that site1's forecast value has the explicit probabilistic values provided
    assert fv_site1.probabilistic_values == prob_values

    # Assert that site2's forecast value uses the default (empty dictionary)
    forecast_values = get_forecast_values_fast(db_session, site_uuids[1], d0)
    fv_site2 = forecast_values[0]
    assert fv_site2.probabilistic_values == {}
