""" Get forecast values from the database

This replace latest_forecast_values.py
"""
from pvsite_datamodel.read.forecast import get_last_forecast_uuid
from pvsite_datamodel.read.latest_forecast_values import get_latest_forecast_values_by_site

import logging
import datetime as dt
import uuid


from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import ForecastValueSQL

logger = logging.getLogger(__name__)


def get_forecast_values_by_site(
    session: Session,
    site_uuids: list[uuid.UUID],
    start_utc: dt.datetime,
    end_utc: dt.datetime | None = None,
    created_by: dt.datetime | None = None,
    created_after: dt.datetime | None = None,
    forecast_horizon_minutes: int | None = None,
    day_ahead_hours: int | None = None,
    day_ahead_timezone_delta_hours: float | None = 0,
    model_name: str | None = None,
) -> dict[uuid.UUID, list[ForecastValueSQL]]:
    """
    Get forecast values

    The ideas is to split this query into separate ones
    1. Get the latest forecasts (not the forecast values)
    2. Get forecast values in the future, this should be quicker
        because only one forecast needs to be loaded
    3. Get forecast values in the past

    :param session:
    :param site_uuids:
    :param start_utc:
    :param end_utc:
    :param created_by:
    :param created_after:
    :param forecast_horizon_minutes:
    :param day_ahead_hours:
    :param day_ahead_timezone_delta_hours:
    :param model_name:
    :return:
    """

    # 1.
    # forecast  uuids from the last forecast
    forecast_uuids = get_last_forecast_uuid(
        session=session,
        model_name=model_name,
        site_uuids=site_uuids,
        day_ahead_hours=day_ahead_hours,
        day_ahead_timezone_delta_hours=day_ahead_timezone_delta_hours,
        created_after=dt.datetime.now()-dt.timedelta(days=1),
        created_before=created_by,
    )
    logger.debug("Found forecast uuids for future period")

    if end_utc is not None:
        future_start_datetime = min([dt.datetime.now(dt.timezone.utc), end_utc])
    else:
        future_start_datetime = dt.datetime.now()
    future_end_datetime = end_utc

    # 2. Get future forecast values
    logger.debug(f"{future_start_datetime} - {future_end_datetime} for future forecasts")
    future_forecast_values = get_latest_forecast_values_by_site(
        session=session,
        site_uuids=site_uuids,
        start_utc=future_start_datetime,
        end_utc=future_end_datetime,
        sum_by=None,
        created_by=created_by,
        created_after=created_after,
        forecast_horizon_minutes=forecast_horizon_minutes,
        day_ahead_hours=day_ahead_hours,
        day_ahead_timezone_delta_hours=day_ahead_timezone_delta_hours,
        model_name=model_name,
        forecast_uuids=forecast_uuids,
    )

    logger.debug(f"{len(future_forecast_values)=}")

    if end_utc is not None:
        past_end_datetime = min([dt.datetime.now(dt.timezone.utc), end_utc])
    else:
        past_end_datetime = dt.datetime.now()

    # 3. Get past forecast values
    if forecast_horizon_minutes is None:
        forecast_horizon_minutes_upper_limit = 60
    else:
        forecast_horizon_minutes_upper_limit = forecast_horizon_minutes + 60

    logger.debug(f"{start_utc} - {past_end_datetime} for past forecasts")
    past_forecast_values = get_latest_forecast_values_by_site(
        session=session,
        site_uuids=site_uuids,
        start_utc=start_utc,
        end_utc=past_end_datetime,
        sum_by=None,
        created_by=created_by,
        created_after=created_after,
        forecast_horizon_minutes=forecast_horizon_minutes,
        forecast_horizon_minutes_upper_limit=forecast_horizon_minutes_upper_limit,
        day_ahead_hours=day_ahead_hours,
        day_ahead_timezone_delta_hours=day_ahead_timezone_delta_hours,
        model_name=model_name,
        # forecast_uuids=forecast_uuids,
    )

    # Combine past and future forecast values
    combined_forecast_values = {}
    for site_uuid in site_uuids:
        combined_forecast_values[site_uuid] = past_forecast_values.get(
            site_uuid, []
        ) + future_forecast_values.get(site_uuid, [])

    return combined_forecast_values


