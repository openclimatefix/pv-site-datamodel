"""Functions for reading from latest_forecast_values table."""

import datetime as dt
import uuid
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import ForecastValueSQL


def get_forecast_values_by_site_latest(
    session: Session,
    site_uuids: List[uuid.UUID],
    start_utc: Optional[dt.datetime] = None,
) -> Dict[uuid.UUID, List[ForecastValueSQL]]:
    """Get the forecast values by input sites, get the lastest value.

    This reads the ForecastValueSQL table

    :param session: The sqlalchemy database session
    :param site_uuids: list of site_uuids for which to fetch latest forecast values
    :param start_utc: filters on forecast values target_time >= start_utc
    """
    query = session.query(ForecastValueSQL).distinct(
        ForecastValueSQL.site_uuid, ForecastValueSQL.start_utc
    )

    if start_utc is not None:
        query = query.filter(ForecastValueSQL.start_utc >= start_utc)

    # Filter the query on the desired sites
    query = query.filter(ForecastValueSQL.site_uuid.in_(site_uuids))

    query.order_by(
        ForecastValueSQL.site_uuid,
        ForecastValueSQL.start_utc,
        ForecastValueSQL.created_utc.desc(),
    )

    # query results
    forecast_values = query.all()

    output_dict: Dict[uuid.UUID, List[ForecastValueSQL]] = {}

    for site_uuid in site_uuids:
        site_latest_forecast_values: List[ForecastValueSQL] = [
            fv for fv in forecast_values if fv.forecast.site_uuid == site_uuid
        ]

        output_dict[site_uuid] = site_latest_forecast_values

    return output_dict
