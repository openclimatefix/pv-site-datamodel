from pvsite_datamodel.read.forecast import get_forecasts
from pvsite_datamodel.read.latest_forecast_values import get_latest_forecast_values_by_site

import logging
import datetime as dt
import uuid

from pvsite_datamodel.sqlmodels import ForecastSQL, MLModelSQL
from sqlalchemy import func, text

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

    The ideas is to split this query into seperate ones
    1. Get the latest forecasts (not the forecast values)
    2. Get forecast values in the future, this should be quicker because only one forecast needs to be loaded
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

    now = dt.datetime.now(dt.timezone.utc)


    # 1.
    future_start_datetime = now
    future_created_after = now - dt.timedelta(days=2)

    max_horizon_minutes = get_max_horizon_minutes(
        session=session,
        created_after=now- dt.timedelta(days=1),
        end_utc=end_utc,
        model_name=model_name,
        site_uuids=site_uuids,
        start_utc=now)
    print(max_horizon_minutes)

    # forecast  uuids from the last forecast
    forecast_uuids = get_forecasts(
        session=session,
        created_after=future_created_after,
        end_utc=end_utc,
        model_name=model_name,
        site_uuids=site_uuids,
        start_utc=future_start_datetime,
        day_ahead_hours=day_ahead_hours,
        day_ahead_timezone_delta_hours=day_ahead_timezone_delta_hours,
        horizon_minutes=max_horizon_minutes,
    )
    print("*****")
    print(f"Found {len(forecast_uuids)} forecast uuids for future period")
    print("*****")

    if end_utc is not None:
        future_start_datetime = min([dt.datetime.now(dt.timezone.utc), end_utc])
    else:
        future_start_datetime = dt.datetime.now()
    future_end_datetime = end_utc

    # 2. Get future forecast values
    print(f"{future_start_datetime} - {future_end_datetime} for future forecasts")
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

    print("*****")
    print(f"{len(future_forecast_values)=}")
    print("*****")

    if end_utc is not None:
        past_end_datetime = min([dt.datetime.now(dt.timezone.utc), end_utc])
    else:
        past_end_datetime = dt.datetime.now()

    # 3. Get past forecast values
    if forecast_horizon_minutes is None:
        forecast_horizon_minutes_upper_limit = 60
    else:
        forecast_horizon_minutes_upper_limit = forecast_horizon_minutes + 60

    if day_ahead_hours is not None:
        forecast_uuids = get_forecasts(
            session=session,
            created_after=created_after,
            end_utc=past_end_datetime,
            model_name=model_name,
            site_uuids=site_uuids,
            start_utc=start_utc,
            day_ahead_hours=day_ahead_hours,
            day_ahead_timezone_delta_hours=day_ahead_timezone_delta_hours,
        )
    else:
        forecast_uuids=None

    print(f"{start_utc} - {past_end_datetime} for past forecasts")
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
        forecast_uuids=forecast_uuids,
    )

    print(f"{len(past_forecast_values)=}")

    # Combine past and future forecast values
    combined_forecast_values = {}
    for site_uuid in site_uuids:
        combined_forecast_values[site_uuid] = past_forecast_values.get(
            site_uuid, []
        ) + future_forecast_values.get(site_uuid, [])

    return combined_forecast_values




def get_max_horizon_minutes(
    session,
    site_uuids,
    start_utc,
    created_after: dt.datetime | None = None,
    end_utc: dt.datetime | None = None,
    model_name: str | None = None,
):
    """Get forecast UUIDs for the given sites and conditions."""

    query = session.query(func.max(ForecastValueSQL.horizon_minutes))
    query = query.join(ForecastSQL)
    query = query.filter(ForecastSQL.location_uuid.in_(site_uuids))

    if created_after is not None:
        query = query.filter(ForecastSQL.created_utc >= created_after)
        query = query.filter(ForecastSQL.timestamp_utc >= created_after)

    # join with Forecast Value
    if model_name is not None:
        query = query.join(MLModelSQL, ForecastValueSQL.ml_model_uuid == MLModelSQL.model_uuid)
        query = query.filter(MLModelSQL.name == model_name)

    query = query.filter(ForecastValueSQL.start_utc >= start_utc)

    if end_utc is not None:
        query = query.filter(ForecastValueSQL.start_utc < end_utc)

    max_horizon_minutes = query.all()

    return max_horizon_minutes[0][0]
