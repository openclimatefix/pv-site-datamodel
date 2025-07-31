""" Read Foreacsts from database """
from datetime import datetime
from pvsite_datamodel import ForecastSQL, ForecastValueSQL
from pvsite_datamodel.sqlmodels import MLModelSQL
import uuid
import logging

from sqlalchemy import Date, text


log = logging.getLogger(__name__)


def get_last_forecast_uuid(
    session,
    site_uuid: str | uuid.UUID,
    start_utc: datetime | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    end_utc: datetime | None = None,
    model_name: str | None = None,
    horizon_minutes: int | None = None,
) -> list[str | uuid.UUID] | None:
    """Get the last forecast UUIDs

    :param session: database session
    :param site_uuid: UUID of the site for which to get the forecast
    :param start_utc: optional filter on start datetime
    :param created_after: optional filter on creation datetime (inclusive)
    :param created_before: optional filter on creation datetime (exclusive)
    :param end_utc: optional filter on end datetime (exclusive)
    :param model_name: optional filter on model name
    :param horizon_minutes: optional filter on forecast horizon in minutes
    :return: list of forecast UUIDs or None if no forecasts found
    """

    query = session.query(ForecastValueSQL.forecast_uuid)
    query = query.join(ForecastSQL)
    query = query.filter(ForecastSQL.location_uuid == site_uuid)

    if created_after is not None:
        query = query.filter(ForecastSQL.created_utc >= created_after)
        query = query.filter(ForecastSQL.timestamp_utc >= created_after)

    if created_before is not None:
        query = query.filter(ForecastSQL.created_utc < created_before)
        query = query.filter(ForecastSQL.timestamp_utc < created_before)

    if model_name is not None:
        query = query.join(MLModelSQL, ForecastValueSQL.ml_model_uuid == MLModelSQL.model_uuid)
        query = query.filter(MLModelSQL.name == model_name)

    if start_utc is not None:
        query = query.filter(ForecastValueSQL.start_utc >= start_utc)

    if end_utc is not None:
        query = query.filter(ForecastValueSQL.start_utc < end_utc)

    if horizon_minutes is not None:
        query = query.filter(ForecastValueSQL.horizon_minutes == horizon_minutes)

    query = query.order_by(ForecastSQL.timestamp_utc.desc())
    query = query.limit(1)

    rows = query.all()

    if len(rows) == 0:
        log.warning(
            f"Could not find any forecasts for {site_uuid} at {start_utc} "
            f"with {created_after=} and {end_utc=}"
        )
        return None

    return [r[0] for r in rows]


def get_day_ahead_forecast_uuids(
    session,
    site_uuid: str | uuid.UUID,
    start_utc: datetime | None = None,
    end_utc: datetime | None = None,
    day_ahead_hours: int = 9,
    day_ahead_timezone_delta_hours: float | None = 0,
    model_name: str | None = None,
):
    """Get the forecast uuids for the day ahead forecasts"""

    query = session.query(ForecastSQL.forecast_uuid)

    # lets get distinct date
    query = query.distinct(ForecastSQL.created_utc.cast(Date))

    # filter on site_uuid
    query = query.filter(ForecastSQL.location_uuid == site_uuid)

    # filter on start and end
    if start_utc is not None:
        query = query.filter(ForecastSQL.created_utc >= start_utc)
    if end_utc is not None:
        query = query.filter(ForecastSQL.created_utc <= end_utc)

    if model_name is not None:
        query = query.join(ForecastValueSQL)
        query = query.join(MLModelSQL)
        query = query.filter(MLModelSQL.name == model_name)

        # we only need to look at one horizon_minutes,
        # as we are only getting one forecast value
        # this speeds up the query ~x100
        query = query.filter(ForecastValueSQL.horizon_minutes == 15)

        if start_utc is not None:
            query = query.filter(ForecastValueSQL.created_utc >= start_utc)
        if end_utc is not None:
            query = query.filter(ForecastValueSQL.created_utc <= end_utc)

    query = query.filter(
        text(
            "extract(hour from forecasts.created_utc) "
            f"< {day_ahead_hours - day_ahead_timezone_delta_hours}"
        )
    )
    # order by
    query = query.order_by(ForecastSQL.created_utc.cast(Date), ForecastSQL.created_utc.desc())

    rows = query.all()
    return [r[0] for r in rows]
