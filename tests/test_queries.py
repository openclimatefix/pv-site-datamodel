"""Test typical ORM queries."""

import datetime as dt

from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL, LocationSQL


def _add_forecast_value(session, forecast, power: int, ts):
    session.add(
        ForecastValueSQL(
            forecast_uuid=forecast.forecast_uuid,
            forecast_power_kw=power,
            start_utc=ts,
            end_utc=ts + dt.timedelta(minutes=5),
        ),
    )


def test_get_latest_forecasts(db_session, engine, sites, forecast_valid_site):
    """Get the values of the latest forecast for given pv sites.

    The query looks like this:

    SELECT f.site_uuid, fv.forecast_power_kw, fv.start_utc
    FROM (
        SELECT
        DISTINCT ON (site_uuid)
            forecast_uuid, site_uuid
        FROM forecasts
        where site_uuid IN ('04b3d67f-af48-42f7-ac0f-9d07d4dd84f6', ...)
        ORDER BY site_uuid, timestamp_utc DESC
    ) AS f
    JOIN forecast_values AS fv
      ON fv.forecast_uuid = f.forecast_uuid
    """
    # Get some sites.
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
        timestamp_utc=dt.datetime(2000, 1, 2),
    )
    s2_f1 = ForecastSQL(
        location_uuid=s2,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )

    db_session.add_all([s1_f1, s1_f2, s2_f1])
    db_session.commit()

    # site 1 forecast 1
    _add_forecast_value(db_session, s1_f1, 1.0, dt.datetime(2000, 1, 1))
    _add_forecast_value(db_session, s1_f1, 2.0, dt.datetime(2000, 1, 1, 1))
    _add_forecast_value(db_session, s1_f1, 3.0, dt.datetime(2000, 1, 1, 2))
    # site 1 forecast 2
    _add_forecast_value(db_session, s1_f2, 4.0, dt.datetime(2000, 1, 1, 2))
    _add_forecast_value(db_session, s1_f2, 5.0, dt.datetime(2000, 1, 1, 3))
    _add_forecast_value(db_session, s1_f2, 6.0, dt.datetime(2000, 1, 1, 4))
    # Site 2 forecast 1
    _add_forecast_value(db_session, s2_f1, 7.0, dt.datetime(2000, 1, 1))
    _add_forecast_value(db_session, s2_f1, 8.0, dt.datetime(2000, 1, 1, 1))
    _add_forecast_value(db_session, s2_f1, 9.0, dt.datetime(2000, 1, 1, 2))
    db_session.commit()

    # Subquery for the forecasts.
    subquery = (
        db_session.query(ForecastSQL)
        .distinct(ForecastSQL.location_uuid)
        .filter(ForecastSQL.location_uuid.in_(site_uuids))
        .order_by(
            ForecastSQL.location_uuid,
            ForecastSQL.timestamp_utc.desc(),
        )
    )

    assert subquery.count() == 2

    # Final query for the forecast values.
    subquery = subquery.subquery()
    values = (
        db_session.query(subquery, ForecastValueSQL)
        .join(ForecastValueSQL)
        .order_by(subquery.c.timestamp_utc, ForecastValueSQL.start_utc)
    )

    expected = [7, 8, 9, 4, 5, 6]
    assert [v.ForecastValueSQL.forecast_power_kw for v in values] == expected
