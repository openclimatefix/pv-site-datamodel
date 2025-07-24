from datetime import datetime
from pvsite_datamodel import ForecastSQL, ForecastValueSQL
from pvsite_datamodel.sqlmodels import MLModelSQL


def get_forecasts(
    session,
    site_uuids,
    start_utc,
    created_after: datetime | None = None,
    end_utc: datetime | None = None,
    model_name: str | None = None,
):
    """Get forecast UUIDs for the given sites and conditions."""

    query = session.query(ForecastSQL.forecast_uuid)
    query = query.distinct(ForecastSQL.location_uuid)
    query = query.filter(ForecastSQL.location_uuid.in_(site_uuids))

    if created_after is not None:
        query = query.filter(ForecastSQL.created_utc >= created_after)

    # join with Forecast Value
    query = query.join(ForecastValueSQL)
    if model_name is not None:
        query = query.join(MLModelSQL, ForecastValueSQL.ml_model_uuid == MLModelSQL.model_uuid)
        query = query.filter(MLModelSQL.name == model_name)

    query = query.filter(ForecastValueSQL.start_utc >= start_utc)

    if end_utc is not None:
        query = query.filter(ForecastValueSQL.start_utc < end_utc)

    query = query.order_by(ForecastSQL.location_uuid, ForecastSQL.created_utc.desc())
    forecast_uuids = [row.forecast_uuid for row in query.all()]

    return forecast_uuids
