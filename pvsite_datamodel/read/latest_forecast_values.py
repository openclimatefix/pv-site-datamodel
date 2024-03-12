"""Functions for reading forecasts."""

import datetime as dt
import uuid
from typing import List, Optional, Union

from sqlalchemy import func
from sqlalchemy.orm import Session

from pvsite_datamodel.pydantic_models import ForecastValueSum
from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL, SiteSQL


def get_latest_forecast_values_by_site(
    session: Session,
    site_uuids: list[uuid.UUID],
    start_utc: dt.datetime,
    sum_by: Optional[str] = None,
    created_by: Optional[dt.datetime] = None,
    forecast_horizon_minutes: Optional[int] = None,
) -> Union[dict[uuid.UUID, list[ForecastValueSQL]], List[ForecastValueSum]]:
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

    :param session: The sqlalchemy database session
    :param site_uuids: list of site_uuids for which to fetch latest forecast values
    :param start_utc: filters on forecast values target_time >= start_utc
    :param created_by: filter on forecast values created time <= created_by
    :param sum_by: optional, sum the forecast values by this column
    :param forecast_horizon_minutes, optional, filter on forecast horizon minutes
    """

    if sum_by not in ["total", "dno", "gsp", None]:
        raise ValueError(f"sum_by must be one of ['total', 'dno', 'gsp'], not {sum_by}")

    query = (
        session.query(ForecastValueSQL)
        .distinct(
            ForecastSQL.site_uuid,
            ForecastValueSQL.start_utc,
        )
        .join(ForecastSQL)
        .filter(
            ForecastValueSQL.start_utc >= start_utc,
            ForecastSQL.site_uuid.in_(site_uuids),
        )
    )

    if created_by is not None:
        query = query.filter(ForecastValueSQL.created_utc <= created_by)

    if forecast_horizon_minutes is not None:
        query = query.filter(ForecastValueSQL.horizon_minutes == forecast_horizon_minutes)

    query = query.order_by(
        ForecastSQL.site_uuid,
        ForecastValueSQL.start_utc,
        ForecastSQL.timestamp_utc.desc(),
    )

    if sum_by is None:
        # query results
        forecast_values = query.all()

        output_dict: dict[uuid.UUID, list[ForecastValueSQL]] = {}

        for site_uuid in site_uuids:
            site_latest_forecast_values: list[ForecastValueSQL] = [
                fv for fv in forecast_values if fv.forecast.site_uuid == site_uuid
            ]

            output_dict[site_uuid] = site_latest_forecast_values

        return output_dict
    else:
        subquery = query.subquery()

        group_by_variables = [subquery.c.start_utc]
        if sum_by == "dno":
            group_by_variables.append(SiteSQL.dno)
        if sum_by == "gsp":
            group_by_variables.append(SiteSQL.gsp)
        query_variables = group_by_variables.copy()
        query_variables.append(func.sum(subquery.c.forecast_power_kw))

        query = session.query(*query_variables)
        query = query.join(ForecastSQL, ForecastSQL.forecast_uuid == subquery.c.forecast_uuid)
        query = query.join(SiteSQL)
        query = query.group_by(*group_by_variables)
        query = query.order_by(*group_by_variables)
        forecasts_raw = query.all()

        forecasts: List[ForecastValueSum] = []
        for forecast_raw in forecasts_raw:
            if len(forecast_raw) == 2:
                generation = ForecastValueSum(
                    start_utc=forecast_raw[0], power_kw=forecast_raw[1], name="total"
                )
            else:
                generation = ForecastValueSum(
                    start_utc=forecast_raw[0], power_kw=forecast_raw[2], name=forecast_raw[1]
                )
            forecasts.append(generation)

    return forecasts
