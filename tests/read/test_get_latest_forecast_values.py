import datetime as dt
from typing import Optional

import pytest

from pvsite_datamodel import ForecastSQL, ForecastValueSQL, SiteSQL
from pvsite_datamodel.read import get_latest_forecast_values_by_site


def _add_forecast_value(
    session,
    forecast,
    power: int,
    ts,
    horizon_minutes: Optional[int] = None,
    created_utc: Optional[dt.datetime] = None,
):
    fv = ForecastValueSQL(
        forecast_uuid=forecast.forecast_uuid,
        forecast_power_kw=power,
        start_utc=ts,
        end_utc=ts + dt.timedelta(minutes=5),
    )
    if horizon_minutes:
        fv.forecast_horizon_minutes = horizon_minutes

    if created_utc:
        fv.created_utc = created_utc
    session.add(fv)


def test_get_latest_forecast_values(db_session, sites):
    site_uuids = [site.site_uuid for site in db_session.query(SiteSQL.site_uuid).limit(2)]

    s1, s2 = site_uuids

    forecast_version = "123"

    # Make sure we have some forecasts in the DB
    s1_f1 = ForecastSQL(
        site_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )
    s1_f2 = ForecastSQL(
        site_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1, 0, 10),
    )
    s2_f1 = ForecastSQL(
        site_uuid=s2,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )

    db_session.add_all([s1_f1, s1_f2, s2_f1])
    db_session.commit()

    d0 = dt.datetime(2000, 1, 1, 0)
    d1 = dt.datetime(2000, 1, 1, 1)
    d2 = dt.datetime(2000, 1, 1, 2)
    d3 = dt.datetime(2000, 1, 1, 3)
    d4 = dt.datetime(2000, 1, 1, 4)

    # site 1 forecast 1
    _add_forecast_value(db_session, s1_f1, 1.0, d0, horizon_minutes=0)
    _add_forecast_value(db_session, s1_f1, 2.0, d1, horizon_minutes=60)
    _add_forecast_value(db_session, s1_f1, 3.0, d2, horizon_minutes=120)

    # site 1 forecast 2
    _add_forecast_value(db_session, s1_f2, 4.0, d2, horizon_minutes=60)
    _add_forecast_value(db_session, s1_f2, 5.0, d3, horizon_minutes=120)
    _add_forecast_value(db_session, s1_f2, 6.0, d4, horizon_minutes=180)

    # Site 2 forecast 1
    _add_forecast_value(db_session, s2_f1, 7.0, d0, horizon_minutes=0)
    _add_forecast_value(db_session, s2_f1, 8.0, d1, horizon_minutes=60)
    _add_forecast_value(db_session, s2_f1, 9.0, d2, horizon_minutes=120)
    db_session.commit()

    latest_forecast = get_latest_forecast_values_by_site(db_session, site_uuids, d1)

    expected = {
        s1: [(d1, 2), (d2, 4), (d3, 5), (d4, 6)],
        s2: [(d1, 8), (d2, 9)],
    }

    assert list(sorted(latest_forecast.keys())) == list(sorted(expected.keys()))

    for site_uuid, forecast_values in latest_forecast.items():
        # Format the values in a way that we can compare them.
        values_as_tuple = [(v.start_utc, v.forecast_power_kw) for v in forecast_values]

        assert values_as_tuple == expected[site_uuid]

    latest_forecast = get_latest_forecast_values_by_site(
        session=db_session,
        site_uuids=site_uuids,
        start_utc=d1,
        sum_by="total",
        created_by=dt.datetime.now() - dt.timedelta(hours=3),
    )
    assert len(latest_forecast) == 0

    latest_forecast = get_latest_forecast_values_by_site(
        session=db_session, site_uuids=site_uuids, start_utc=d1, sum_by="total"
    )
    assert len(latest_forecast) == 4

    latest_forecast = get_latest_forecast_values_by_site(
        session=db_session, site_uuids=site_uuids, start_utc=d1, sum_by="dno"
    )
    assert len(latest_forecast) == 4 + 2  # 4 from site 1, 2 from site 2

    latest_forecast = get_latest_forecast_values_by_site(
        session=db_session, site_uuids=site_uuids, start_utc=d2, sum_by="gsp"
    )
    assert len(latest_forecast) == 3 + 1  # 3 from site 1, 1 from site 2

    latest_forecast = get_latest_forecast_values_by_site(
        session=db_session, site_uuids=site_uuids, start_utc=d2, forecast_horizon_minutes=60
    )
    assert len(latest_forecast) == 2

    with pytest.raises(ValueError):  # noqa
        _ = get_latest_forecast_values_by_site(
            session=db_session, site_uuids=site_uuids, start_utc=d2, sum_by="bla"
        )


def test_get_latest_forecast_values_with_end_utc(db_session, sites):
    # ****** setup ******
    site_uuids = [site.site_uuid for site in db_session.query(SiteSQL.site_uuid).limit(2)]

    s1, s2 = site_uuids

    forecast_version = "123"

    # Make sure we have some forecasts in the DB
    s1_f1 = ForecastSQL(
        site_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )
    s1_f2 = ForecastSQL(
        site_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1, 0, 10),
    )
    s2_f1 = ForecastSQL(
        site_uuid=s2,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )

    db_session.add_all([s1_f1, s1_f2, s2_f1])
    db_session.commit()

    d0 = dt.datetime(2000, 1, 1, 0)
    d1 = dt.datetime(2000, 1, 1, 1)
    d2 = dt.datetime(2000, 1, 1, 2)
    d3 = dt.datetime(2000, 1, 1, 3)
    d4 = dt.datetime(2000, 1, 1, 4)

    # site 1 forecast 1
    _add_forecast_value(db_session, s1_f1, 1.0, d0, horizon_minutes=0)
    _add_forecast_value(db_session, s1_f1, 2.0, d1, horizon_minutes=60)
    _add_forecast_value(db_session, s1_f1, 3.0, d2, horizon_minutes=120)

    # site 1 forecast 2
    _add_forecast_value(db_session, s1_f2, 4.0, d2, horizon_minutes=60)
    _add_forecast_value(db_session, s1_f2, 5.0, d3, horizon_minutes=120)
    _add_forecast_value(db_session, s1_f2, 6.0, d4, horizon_minutes=180)

    # Site 2 forecast 1
    _add_forecast_value(db_session, s2_f1, 7.0, d0, horizon_minutes=0)
    _add_forecast_value(db_session, s2_f1, 8.0, d1, horizon_minutes=60)
    _add_forecast_value(db_session, s2_f1, 9.0, d2, horizon_minutes=120)
    db_session.commit()

    # ****** setup ******

    latest_forecast = get_latest_forecast_values_by_site(db_session, site_uuids, d1, end_utc=d2)

    expected = {
        s1: [(d1, 2)],
        s2: [(d1, 8)],
    }

    assert list(sorted(latest_forecast.keys())) == list(sorted(expected.keys()))

    for site_uuid, forecast_values in latest_forecast.items():
        # Format the values in a way that we can compare them.
        values_as_tuple = [(v.start_utc, v.forecast_power_kw) for v in forecast_values]

        assert values_as_tuple == expected[site_uuid]


def test_get_latest_forecast_values_day_head(db_session, sites):
    """Test to get DA forecasts"""
    site_uuids = [site.site_uuid for site in db_session.query(SiteSQL.site_uuid).limit(2)]

    s1, s2 = site_uuids

    forecast_version = "123"

    # Make sure we have some forecasts in the DB
    s1_f1 = ForecastSQL(
        site_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )
    s1_f2 = ForecastSQL(
        site_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1, 0, 10),
    )

    db_session.add_all([s1_f1, s1_f2])
    db_session.commit()

    d0 = dt.datetime(2000, 1, 2, 0)
    d1 = dt.datetime(2000, 1, 2, 1)
    d2 = dt.datetime(2000, 1, 2, 2)
    cr1 = dt.datetime(2000, 1, 1, 0)
    cr2 = dt.datetime(2000, 1, 2, 0)

    # site 1 forecast 1
    _add_forecast_value(db_session, s1_f1, 1.0, d0, horizon_minutes=0, created_utc=cr1)
    _add_forecast_value(db_session, s1_f1, 2.0, d1, horizon_minutes=60, created_utc=cr1)
    _add_forecast_value(db_session, s1_f1, 3.0, d2, horizon_minutes=120, created_utc=cr1)

    # site 1 forecast 2
    _add_forecast_value(db_session, s1_f2, 4.0, d0, horizon_minutes=60, created_utc=cr2)
    _add_forecast_value(db_session, s1_f2, 5.0, d1, horizon_minutes=120, created_utc=cr2)
    _add_forecast_value(db_session, s1_f2, 6.0, d2, horizon_minutes=180, created_utc=cr2)

    latest_forecast = get_latest_forecast_values_by_site(
        session=db_session, site_uuids=site_uuids, start_utc=d0, day_ahead_hours=9
    )

    expected = {s1: [(d0, 1), (d1, 2), (d2, 3)], s2: []}

    assert list(sorted(latest_forecast.keys())) == list(sorted(expected.keys()))

    for site_uuid, forecast_values in latest_forecast.items():
        # Format the values in a way that we can compare them.
        values_as_tuple = [(v.start_utc, v.forecast_power_kw) for v in forecast_values]

        assert len(values_as_tuple) == len(
            expected[site_uuid]
        ), f"{len(values_as_tuple)=}, {len(expected[site_uuid])=}"
        assert values_as_tuple == expected[site_uuid], f"{values_as_tuple=}, {expected[site_uuid]=}"


def test_get_latest_forecast_values_day_head_with_timezone(db_session, sites):
    """Test to get DA forecasts in a different timezone"""
    site_uuids = [site.site_uuid for site in db_session.query(SiteSQL.site_uuid).limit(2)]

    s1, s2 = site_uuids

    forecast_version = "123"

    # Make sure we have some forecasts in the DB
    s1_f1 = ForecastSQL(
        site_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )
    s1_f2 = ForecastSQL(
        site_uuid=s1,
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
    _add_forecast_value(db_session, s1_f1, 1.0, d0, created_utc=cr1)
    _add_forecast_value(db_session, s1_f1, 2.0, d1, created_utc=cr1)
    _add_forecast_value(db_session, s1_f1, 3.0, d2, created_utc=cr1)

    # site 1 forecast 2
    _add_forecast_value(db_session, s1_f2, 4.0, d0, created_utc=cr2)
    _add_forecast_value(db_session, s1_f2, 5.0, d1, created_utc=cr2)
    _add_forecast_value(db_session, s1_f2, 6.0, d2, created_utc=cr2)

    latest_forecast = get_latest_forecast_values_by_site(
        session=db_session,
        site_uuids=site_uuids,
        start_utc=d0,
        day_ahead_hours=9,
        day_ahead_timezone_delta_hours=4.5,
    )

    expected = {s1: [(d0, 1), (d1, 5), (d2, 6)], s2: []}

    assert list(sorted(latest_forecast.keys())) == list(sorted(expected.keys()))

    for site_uuid, forecast_values in latest_forecast.items():
        # Format the values in a way that we can compare them.
        values_as_tuple = [(v.start_utc, v.forecast_power_kw) for v in forecast_values]

        assert len(values_as_tuple) == len(
            expected[site_uuid]
        ), f"{len(values_as_tuple)=}, {len(expected[site_uuid])=}"
        assert values_as_tuple == expected[site_uuid], f"{values_as_tuple=}, {expected[site_uuid]=}"
