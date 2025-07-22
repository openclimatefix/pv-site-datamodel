"""Functions for reading forecasts."""

import datetime as dt
import uuid

from sqlalchemy import func, text
from sqlalchemy.orm import Session, contains_eager

from pvsite_datamodel.pydantic_models import ForecastValueSum
from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL, LocationSQL, MLModelSQL


def get_latest_forecast_values_by_site(
    session: Session,
    site_uuids: list[uuid.UUID],
    start_utc: dt.datetime,
    end_utc: dt.datetime | None = None,
    sum_by: str | None = None,
    created_by: dt.datetime | None = None,
    created_after: dt.datetime | None = None,
    forecast_horizon_minutes: int | None = None,
    day_ahead_hours: int | None = None,
    day_ahead_timezone_delta_hours: float | None = 0,
    model_name: str | None = None,
) -> dict[uuid.UUID, list[ForecastValueSQL]] | list[ForecastValueSum]:
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
    :param site_uuids: list of site_uuids for which to fetch latest forecast values
    :param start_utc: filters on forecast values target_time >= start_utc
    :param end_utc: optional, filters on forecast values target_time < end_utc
    :param created_by: filter on forecast values created time <= created_by
    :param created_after: optional, filter on forecast values created time >= created_after
    :param sum_by: optional, sum the forecast values by this column
    :param forecast_horizon_minutes, optional, filter on forecast horizon minutes. We
        return any forecast with forecast horizon mintues >= this value.
        For example, for forecast_horizon_minutes==90, the latest forecast great or equal to
        forecast_horizon_minutes=90 will be loaded.
    :param day_ahead_hours: optional, filter on forecast values on creattion time.
        If day_ahead_hours=9, we only get forecasts made before 9 o'clock the day before.
    :param day_ahead_timezone_delta_hours: optional, the timezone delta in hours.
        As datetimes are stored in UTC, we need to adjust the start_utc when looking at day
        ahead forecast. For example a forecast made a 04:00 UTC for 20:00 UTC for India,
        is actually a day ahead forcast, as India is 5.5 hours ahead on UTC
    :param model_name: optional, filter on forecast values with this model name
    """
    if sum_by not in ["total", "dno", "gsp", None]:
        raise ValueError(f"sum_by must be one of ['total', 'dno', 'gsp'], not {sum_by}")

    if day_ahead_timezone_delta_hours is not None:
        # we use mintues and sql cant handle .5 hours (or any decimals)
        day_ahead_timezone_delta_minute = int(day_ahead_timezone_delta_hours * 60)

    query = (
        session.query(ForecastValueSQL)
        .distinct(
            ForecastSQL.location_uuid,
            ForecastValueSQL.start_utc,
        )
        .join(ForecastSQL)
        .filter(
            ForecastValueSQL.start_utc >= start_utc,
            ForecastSQL.location_uuid.in_(site_uuids),
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

    # speed up query, so all information is gather in one query, rather than lots of little ones
    query = query.options(contains_eager(ForecastValueSQL.forecast)).populate_existing()

    query = query.order_by(
        ForecastSQL.location_uuid,
        ForecastValueSQL.start_utc,
        ForecastSQL.timestamp_utc.desc(),
        ForecastSQL.created_utc.desc(),
    )

    if sum_by is None:
        # query results
        forecast_values = query.all()

        output_dict: dict[uuid.UUID, list[ForecastValueSQL]] = {}

        for site_uuid in site_uuids:
            site_latest_forecast_values: list[ForecastValueSQL] = [
                fv for fv in forecast_values if fv.forecast.location_uuid == site_uuid
            ]

            output_dict[site_uuid] = site_latest_forecast_values

        return output_dict
    else:
        subquery = query.subquery()

        group_by_variables = [subquery.c.start_utc]
        if sum_by == "dno":
            group_by_variables.append(LocationSQL.dno)
        if sum_by == "gsp":
            group_by_variables.append(LocationSQL.gsp)
        query_variables = group_by_variables.copy()
        query_variables.append(func.sum(subquery.c.forecast_power_kw))

        query = session.query(*query_variables)
        query = query.join(ForecastSQL, ForecastSQL.forecast_uuid == subquery.c.forecast_uuid)
        query = query.join(LocationSQL)
        query = query.group_by(*group_by_variables)
        query = query.order_by(*group_by_variables)
        forecasts_raw = query.all()

        forecasts: list[ForecastValueSum] = []
        for forecast_raw in forecasts_raw:
            if len(forecast_raw) == 2:
                generation = ForecastValueSum(
                    start_utc=forecast_raw[0],
                    power_kw=forecast_raw[1],
                    name="total",
                )
            else:
                generation = ForecastValueSum(
                    start_utc=forecast_raw[0],
                    power_kw=forecast_raw[2],
                    name=forecast_raw[1],
                )
            forecasts.append(generation)

    return forecasts
