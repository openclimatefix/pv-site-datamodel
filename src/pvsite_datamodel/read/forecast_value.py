""" Get forecast values from the database

This replace latest_forecast_values.py
"""
import datetime as dt
import logging
import uuid

from sqlalchemy import text
from sqlalchemy.orm import Session

from pvsite_datamodel.read.forecast import get_last_forecast_uuid
from pvsite_datamodel.sqlmodels import ForecastSQL, MLModelSQL
from pvsite_datamodel.sqlmodels import ForecastValueSQL

logger = logging.getLogger(__name__)


def get_forecast_values_fast(
    session: Session,
    site_uuid: uuid.UUID | str,
    start_utc: dt.datetime,
    end_utc: dt.datetime | None = None,
    created_by: dt.datetime | None = None,
    created_after: dt.datetime | None = None,
    forecast_horizon_minutes: int | None = None,
    model_name: str | None = None,
) -> list[ForecastValueSQL]:
    """
    Get forecast values

    The ideas is to split this query into separate ones
    1. Get the latest forecasts (not the forecast values)
    2. Get forecast values uuids in the future, this should be quicker
        because only one forecast needs to be loaded
    3. Get forecast values uuids in the past
    4. Get the actual forecast values

    :param session: Database sessions
    :param site_uuid: The site UUID for which to fetch forecast values
    :param start_utc: filters on forecast values start_utc >= start_utc
    :param end_utc: optional filter on forecast values start_utc < end_utc
    :param created_by: optional filter on forecast values created time <= created_by
    :param created_after: optional filter on forecast values created time >= created_after
    :param forecast_horizon_minutes: optional filter on forecast horizon minutes.
    :param model_name: optional filter on forecast values with this model name
    :return: list of forecast value SQL objects
    """

    # TODO add day ahead options

    # 1. forecast  uuids from the last forecast
    forecast_uuids = get_last_forecast_uuid(
        session=session,
        model_name=model_name,
        site_uuid=site_uuid,
        created_before=created_by,
        start_utc=start_utc,
        end_utc=end_utc,
    )
    logger.debug("Found forecast uuids for future period")

    # 2. Get future forecast values
    future_forecast_values_uuids = get_forecast_values(
        session=session,
        site_uuid=site_uuid,
        start_utc=start_utc,
        end_utc=end_utc,
        created_by=created_by,
        created_after=created_after,
        forecast_horizon_minutes=forecast_horizon_minutes,
        model_name=model_name,
        forecast_uuids=forecast_uuids,
        forecast_value_uuids_only=True,
    )

    logger.debug(f"{len(future_forecast_values_uuids)=}")

    # 3. Get past forecast values
    # get the forecast horizon between forecast_horizon_minutes
    # and forecast_horizon_minutes + 60
    if forecast_horizon_minutes is None:
        forecast_horizon_minutes_upper_limit = 60
    else:
        forecast_horizon_minutes_upper_limit = forecast_horizon_minutes + 60

    logger.debug(f"{start_utc} - {end_utc} for past forecasts")
    past_forecast_values_uuids = get_forecast_values(
        session=session,
        site_uuid=site_uuid,
        start_utc=start_utc,
        end_utc=end_utc,
        created_by=created_by,
        created_after=created_after,
        forecast_horizon_minutes=forecast_horizon_minutes,
        forecast_horizon_minutes_upper_limit=forecast_horizon_minutes_upper_limit,
        model_name=model_name,
        forecast_value_uuids_only=True,
    )

    # Combine past and future forecast values
    forecast_values_uuids = past_forecast_values_uuids + future_forecast_values_uuids

    # 4. get the actual forecast values
    forecast_values = get_forecast_values(
        session=session,
        site_uuid=site_uuid,
        start_utc=start_utc,
        end_utc=end_utc,
        created_by=created_by,
        created_after=created_after,
        forecast_horizon_minutes=forecast_horizon_minutes,
        model_name=model_name,
        forecast_value_uuids=forecast_values_uuids,
    )

    return forecast_values


def get_forecast_values(
    session: Session,
    site_uuid: uuid.UUID | str,
    start_utc: dt.datetime,
    end_utc: dt.datetime | None = None,
    created_by: dt.datetime | None = None,
    created_after: dt.datetime | None = None,
    forecast_horizon_minutes: int | None = None,
    forecast_horizon_minutes_upper_limit: int | None = None,
    day_ahead_hours: int | None = None,
    day_ahead_timezone_delta_hours: float | None = 0,
    model_name: str | None = None,
    forecast_uuids: list[uuid.UUID] | None = None,
    forecast_value_uuids: list[uuid.UUID] | None = None,
    forecast_value_uuids_only: bool = False,
) -> list[uuid.UUID] | list[ForecastValueSQL]:
    """Get the forecast values by input sites, get the latest value.

    Return the forecasts after a given date, but keeping only the latest for a given timestamp.

    The query looks like:

    SELECT
    DISTINCT ON (f.site_uuid, fv.start_utc)
        f.site_uuid,
        fv.forecast_power_kw,
        fv.start_utc
    FROM forecast_values AS fv
    JOIN forecasts AS f
      ON f.forecast_uuid = fv.forecast_uuid
    WHERE fv.start_utc >= <start_utc>
    ORDER BY
        f.site_uuid,
        fv.start_utc,
        f.timestamp_utc DESC
        f.created_utc DESC

    :param session: The sqlalchemy database session
    :param site_uuid: a site_uuid for which to fetch forecast values
    :param start_utc: filters on forecast values target_time >= start_utc
    :param end_utc: optional, filters on forecast values target_time < end_utc
    :param created_by: filter on forecast values created time <= created_by
    :param created_after: optional, filter on forecast values created time >= created_after
    :param forecast_horizon_minutes, optional, filter on forecast horizon minutes. We
        return any forecast with forecast horizon minutes >= this value.
        For example, for forecast_horizon_minutes==90, the latest forecast great or equal to
        forecast_horizon_minutes=90 will be loaded.
    :param forecast_horizon_minutes_upper_limit: optional,
        filter on forecast horizon minutes upper limit.
    :param day_ahead_hours: optional, filter on forecast values on creation time.
        If day_ahead_hours=9, we only get forecasts made before 9 o'clock the day before.
    :param day_ahead_timezone_delta_hours: optional, the timezone delta in hours.
        As datetimes are stored in UTC, we need to adjust the start_utc when looking at day
        ahead forecast. For example a forecast made a 04:00 UTC for 20:00 UTC for India,
        is actually a day ahead forcast, as India is 5.5 hours ahead on UTC
    :param model_name: optional, filter on forecast values with this model name
    :param forecast_uuids: optional, filter on forecast values with these forecast uuids
    :param forecast_value_uuids: optional, filter on forecast values with these forecast value uuids
    :param forecast_value_uuids_only: if True, only return the forecast value uuids, not the full
    """

    if day_ahead_timezone_delta_hours is not None:
        # we use mintues and sql cant handle .5 hours (or any decimals)
        day_ahead_timezone_delta_minute = int(day_ahead_timezone_delta_hours * 60)

    if forecast_value_uuids_only:
        # if we only want the forecast value uuids, we can skip the rest of the query
        query = session.query(ForecastValueSQL.forecast_value_uuid)
    else:
        query = session.query(ForecastValueSQL)

    query = (
        query.distinct(
            ForecastValueSQL.start_utc,
        )
        .join(ForecastSQL)
        .filter(
            ForecastValueSQL.start_utc >= start_utc,
            ForecastSQL.location_uuid == site_uuid,
        )
    )

    # filter on ForecastSQL.timestamp_utc
    timestamp_utc_lower_limit = start_utc - dt.timedelta(hours=48)
    if forecast_horizon_minutes is not None:
        query = query.filter(
            ForecastSQL.timestamp_utc
            >= timestamp_utc_lower_limit - dt.timedelta(minutes=forecast_horizon_minutes)
        )
    elif day_ahead_hours:
        # if day_ahead_hours is set, we filter on the timestamp_utc as well
        query = query.filter(
            ForecastSQL.timestamp_utc >= timestamp_utc_lower_limit - dt.timedelta(hours=24)
        )
    else:
        query = query.filter(ForecastSQL.timestamp_utc >= timestamp_utc_lower_limit)

    if end_utc is not None:
        query = query.filter(ForecastValueSQL.start_utc < end_utc)
        query = query.filter(ForecastSQL.timestamp_utc < end_utc)

    if created_by is not None:
        query = query.filter(ForecastValueSQL.created_utc <= created_by)
        query = query.filter(ForecastSQL.created_utc <= created_by)

    if created_after is not None:
        query = query.filter(ForecastValueSQL.created_utc >= created_after)
        query = query.filter(ForecastSQL.created_utc >= created_after)

    if forecast_horizon_minutes is not None:
        query = query.filter(ForecastValueSQL.horizon_minutes >= forecast_horizon_minutes)

    if forecast_horizon_minutes_upper_limit is not None:
        query = query.filter(
            ForecastValueSQL.horizon_minutes <= forecast_horizon_minutes_upper_limit
        )

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

        query = query.filter(
            ForecastValueSQL.created_utc
            <= text(
                f"date(start_utc + interval '{day_ahead_timezone_delta_minute}' minute "
                f"- interval '1' day) + interval '{day_ahead_hours}' hour "
                f"- interval '{day_ahead_timezone_delta_minute}' minute",
            ),
        )

    if model_name is not None:
        # join with MLModelSQL to filter on model_name
        query = query.join(MLModelSQL)
        query = query.filter(MLModelSQL.name == model_name)

    if forecast_uuids is not None:
        # filter on forecast_uuids
        query = query.filter(ForecastSQL.forecast_uuid.in_(forecast_uuids))

    if forecast_value_uuids is not None:
        # filter on forecast_value_uuids
        query = query.filter(ForecastValueSQL.forecast_value_uuid.in_(forecast_value_uuids))

    query = query.order_by(
        ForecastValueSQL.start_utc,
        ForecastSQL.timestamp_utc.desc(),
        ForecastSQL.created_utc.desc(),
    )

    # query results
    if forecast_value_uuids_only:
        forecast_values = query.all()
        forecast_values_uuids = [row[0] for row in forecast_values]
        return forecast_values_uuids
    else:
        forecast_values: list[ForecastValueSQL] = query.all()
        return forecast_values
