""" Read Foreacsts from database """
from datetime import datetime
from pvsite_datamodel import ForecastSQL, ForecastValueSQL
from pvsite_datamodel.sqlmodels import MLModelSQL
import uuid
import logging

from sqlalchemy import text

log = logging.getLogger(__name__)

def get_last_forecast_uuid(
    session,
    site_uuids: list[str | uuid.UUID],
    start_utc: datetime | None = None,
    created_after: datetime | None = None,
    end_utc: datetime | None = None,
    model_name: str | None = None,
    day_ahead_hours: int | None = None,
    day_ahead_timezone_delta_hours: float | None = 0,
    horizon_minutes: int | None = None,
) -> list[str | uuid.UUID] | None:
    """Get the last forecast UUIDs"""

    query = session.query(ForecastValueSQL.forecast_uuid)
    query = query.join(ForecastSQL)
    query = query.distinct(ForecastSQL.location_uuid)
    query = query.filter(ForecastSQL.location_uuid.in_(site_uuids))

    if created_after is not None:
        query = query.filter(ForecastSQL.created_utc >= created_after)
        query = query.filter(ForecastSQL.timestamp_utc >= created_after)

    if model_name is not None:
        query = query.join(MLModelSQL, ForecastValueSQL.ml_model_uuid == MLModelSQL.model_uuid)
        query = query.filter(MLModelSQL.name == model_name)

    if start_utc is not None:
        query = query.filter(ForecastValueSQL.start_utc >= start_utc)

    if end_utc is not None:
        query = query.filter(ForecastValueSQL.start_utc < end_utc)

    if day_ahead_hours:
        """Filter on forecast values on creation time for day ahead

        For the UK, this means we only get forecasts made before 9 o'clock the day before.
        We do this by
        1. Getting the start_utc, and taking the date. '2024-04-01 20:00:00' -> '2024-04-01'
        2. Minus one day. '2024-04-01' -> '2024-03-31'
        3. Add 9 hours for 9 am. '2024-03-31' -> '2024-03-31 09:00:00'
        4. Then only filters on forecasts made before this time

        For India, which is 5.5 hours ahead of UTC, we need to adjust the timezone delta.
        This is important as as forecast for '2024-04-01 20:00:00' UTC can be made before
        '2024-04-01 04:30:00' UTC and be a day ahead forecast
        """

        # we use minutes and sql cant handle .5 hours (or any decimals)
        day_ahead_timezone_delta_minute = int(day_ahead_timezone_delta_hours * 60)

        query = query.filter(
            ForecastValueSQL.created_utc
            <= text(
                f"date(start_utc + interval '{day_ahead_timezone_delta_minute}' minute "
                f"- interval '1' day) + interval '{day_ahead_hours}' hour "
                f"- interval '{day_ahead_timezone_delta_minute}' minute",
            ),
        )

    if horizon_minutes is not None:
        query = query.filter(ForecastValueSQL.horizon_minutes == horizon_minutes)

    query = query.order_by(ForecastSQL.location_uuid, ForecastValueSQL.start_utc.desc())

    # limit the query by 1
    query = query.limit(len(site_uuids))

    rows = query.all()

    if len(rows) == 0:
        log.warning(f'Could not find any forecasts for {site_uuids} at {start_utc} '
                        f'with {created_after=} and {end_utc=}')
        return None

    return [r[0] for r in rows]


