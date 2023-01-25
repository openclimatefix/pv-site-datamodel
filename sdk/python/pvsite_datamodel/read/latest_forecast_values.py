"""
Functions for reading from latest_forecast_values table
"""

import datetime as dt
import uuid
from typing import Dict, List, Optional

from pvsite_datamodel.sqlmodels import DatetimeIntervalSQL, LatestForecastValueSQL
from sqlalchemy.orm import Query, Session


def get_latest_forecast_values_by_site(
    session: Session, site_uuids: List[uuid.UUID], start_utc: Optional[dt.datetime] = None
) -> Dict[uuid.UUID, List[LatestForecastValueSQL]]:
    """
    Get the latest forecast values by input sites

    :param session: The sqlalchemy database session
    :param site_uuids: list of site_uuids for which to fetch latest forecast values
    :param start_utc: filters on forecast values target_time >= start_utc
    :return: dict containing {site_uuid1: List[LatestForecastValueSQL], site_uuid2: ...}
    """

    # start main query
    query: Query = session.query(LatestForecastValueSQL)

    if start_utc is not None:
        query = query.filter(LatestForecastValueSQL.target_time >= start_utc)

        # also filter on creation time, to speed up things
        created_utc_filter = start_utc - dt.timedelta(days=1)
        query = query.filter(LatestForecastValueSQL.created_utc >= created_utc_filter)

    output_dict: Dict[uuid.UUID, List[LatestForecastValueSQL]] = {}

    for site_uuid in site_uuids:

        # filter on site_uuid
        site_query: Query = query.filter(LatestForecastValueSQL.site_uuid == site_uuid)
        site_query = site_query.join(DatetimeIntervalSQL)

        # order by target time and created time desc
        site_query = site_query.order_by(
            DatetimeIntervalSQL.start_utc,
            LatestForecastValueSQL.created_utc,
        )

        # get all results
        site_latest_forecast_values: List[LatestForecastValueSQL] = site_query.all()

        output_dict[site_uuid] = site_latest_forecast_values

    return output_dict
