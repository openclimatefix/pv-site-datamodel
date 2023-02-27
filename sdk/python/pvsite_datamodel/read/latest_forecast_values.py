"""Functions for reading forecasts."""

import datetime as dt
import uuid

from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL


def get_latest_forecast_values_by_site(
    session: Session,
    site_uuids: list[uuid.UUID],
    start_utc: dt.datetime,
) -> dict[uuid.UUID, list[ForecastValueSQL]]:
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
    """
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
        .order_by(
            ForecastSQL.site_uuid,
            ForecastValueSQL.start_utc,
            ForecastSQL.timestamp_utc.desc(),
        )
    )

    # query results
    forecast_values = query.all()

    output_dict: dict[uuid.UUID, list[ForecastValueSQL]] = {}

    for site_uuid in site_uuids:
        site_latest_forecast_values: list[ForecastValueSQL] = [
            fv for fv in forecast_values if fv.forecast.site_uuid == site_uuid
        ]

        output_dict[site_uuid] = site_latest_forecast_values

    return output_dict
