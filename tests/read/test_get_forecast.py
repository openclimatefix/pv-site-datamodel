import datetime as dt


from pvsite_datamodel import ForecastSQL, ForecastValueSQL, LocationSQL

from pvsite_datamodel.read import get_or_create_model
from pvsite_datamodel.read.forecast import get_day_ahead_forecast_uuids


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





def test_get_forecast_values_day_head(db_session, sites):
    """Test to get DA forecasts"""
    site_uuids = [
        site.location_uuid for site in db_session.query(LocationSQL.location_uuid).limit(2)
    ]

    s1, s2 = site_uuids

    forecast_version = "123"

    cr1 = dt.datetime(2000, 1, 1, 0)
    cr2 = dt.datetime(2000, 1, 2, 0)

    # Make sure we have some forecasts in the DB
    s1_f1 = ForecastSQL(
        location_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
        created_utc=cr1,
    )
    s1_f2 = ForecastSQL(
        location_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1, 0, 10),
        created_utc=cr2,
    )

    db_session.add_all([s1_f1, s1_f2])
    db_session.commit()

    d0 = dt.datetime(2000, 1, 2, 0)
    d1 = dt.datetime(2000, 1, 2, 1)
    d2 = dt.datetime(2000, 1, 2, 2)

    # site 1 forecast 1
    _add_fv(db_session, s1_f1, 1.0, d0, horizon_minutes=15, created_utc=cr1, model_name='test_1')
    _add_fv(db_session, s1_f1, 2.0, d1, horizon_minutes=60, created_utc=cr1, model_name='test_1')
    _add_fv(db_session, s1_f1, 3.0, d2, horizon_minutes=120, created_utc=cr1, model_name='test_1')

    # site 1 forecast 2
    _add_fv(db_session, s1_f2, 4.0, d0, horizon_minutes=15, created_utc=cr2, model_name='test_1')
    _add_fv(db_session, s1_f2, 5.0, d1, horizon_minutes=120, created_utc=cr2, model_name='test_1')
    _add_fv(db_session, s1_f2, 6.0, d2, horizon_minutes=180, created_utc=cr2, model_name='test_1')

    forecast_uuids = get_day_ahead_forecast_uuids(
        session=db_session,
        site_uuid=site_uuids[0],
        start_utc=cr1,
        day_ahead_hours=9,
        model_name='test_1'
    )

    assert len(forecast_uuids) == 2
    assert forecast_uuids[0] == s1_f1.forecast_uuid
    assert forecast_uuids[1] == s1_f2.forecast_uuid


