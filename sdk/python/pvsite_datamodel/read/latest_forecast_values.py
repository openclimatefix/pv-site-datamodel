"""Functions for reading from latest_forecast_values table."""

import datetime as dt
import uuid
from typing import Dict, List, Optional, Union

from sqlalchemy.orm import Query, Session, contains_eager

from pvsite_datamodel.sqlmodels import (
    DatetimeIntervalSQL,
    ForecastValueSQL,
    LatestForecastValueSQL,
    ForecastSQL,
)


def get_latest_forecast_values_by_site(
    session: Session,
    site_uuids: List[uuid.UUID],
    start_utc: Optional[dt.datetime] = None,
) -> Dict[uuid.UUID, List[LatestForecastValueSQL]]:
    """Get the latest forecast values by input sites.

    This reads the LatestForecastValueSQL table

    :param session: The sqlalchemy database session
    :param site_uuids: list of site_uuids for which to fetch latest forecast values
    :param start_utc: filters on forecast values target_time >= start_utc
    :return: dict containing {site_uuid1: List[LatestForecastValueSQL], site_uuid2: ...}
    """
    # start main query
    query: Query = session.query(LatestForecastValueSQL)
    query = query.join(DatetimeIntervalSQL)

    if start_utc is not None:
        query = query.filter(DatetimeIntervalSQL.start_utc >= start_utc)

        # also filter on creation time, to speed up things
        created_utc_filter = start_utc - dt.timedelta(days=1)
        query = query.filter(LatestForecastValueSQL.created_utc >= created_utc_filter)

    output_dict: Dict[uuid.UUID, List[LatestForecastValueSQL]] = {}

    # Filter the query on the desired sites
    query = query.where(LatestForecastValueSQL.site_uuid.in_(site_uuids))

    # order by site, target time and created time desc
    query.order_by(
        LatestForecastValueSQL.site_uuid,
        DatetimeIntervalSQL.start_utc,
        LatestForecastValueSQL.created_utc,
    )

    latest_forecast_values: List[LatestForecastValueSQL] = query.all()

    for site_uuid in site_uuids:
        site_latest_forecast_values: List[LatestForecastValueSQL] = [
            lfv for lfv in latest_forecast_values if lfv.site_uuid == site_uuid
        ]

        output_dict[site_uuid] = site_latest_forecast_values

    return output_dict


def get_forecast_values_by_site_latest(
    session: Session,
    site_uuids: List[uuid.UUID],
    start_utc: Optional[dt.datetime] = None,
) -> Dict[uuid.UUID, List[ForecastValueSQL]]:
    """Get the forecast values by input sites, get the lastest value

    This reads the ForecastValueSQL table

    :param session: The sqlalchemy database session
    :param site_uuids: list of site_uuids for which to fetch latest forecast values
    :param start_utc: filters on forecast values target_time >= start_utc
    :param model, the database table to use, could be 'LatestForecastValueSQL' or ForecastValueSQL
    :return: dict containing {site_uuid1: List[LatestForecastValueSQL], site_uuid2: ...}
    """
    # start main query
    query: Query = session.query(ForecastValueSQL)
    query = query.join(DatetimeIntervalSQL)

    # use distinct if using `ForecastValueSQL`
    query = query.join(ForecastSQL)
    query = query.distinct(ForecastSQL.site_uuid, DatetimeIntervalSQL.start_utc)

    if start_utc is not None:
        query = query.filter(DatetimeIntervalSQL.start_utc >= start_utc)

        # also filter on creation time, to speed up things
        created_utc_filter = start_utc - dt.timedelta(days=1)
        query = query.filter(ForecastValueSQL.created_utc >= created_utc_filter)

    output_dict: Dict[uuid.UUID, List[ForecastValueSQL]] = {}

    # Filter the query on the desired sites
    query = query.where(ForecastSQL.site_uuid.in_(site_uuids))

    # order by site, target time and created time desc
    query.order_by(
        ForecastSQL.site_uuid,
        DatetimeIntervalSQL.start_utc,
        ForecastValueSQL.created_utc,
    )

    # make sure this is all loaded
    query = query.options(contains_eager(ForecastValueSQL.forecast)).populate_existing()
    query = query.options(contains_eager(ForecastValueSQL.datetime_interval)).populate_existing()

    # query results
    forecast_values: List[ForecastValueSQL] = query.all()

    for site_uuid in site_uuids:
        site_latest_forecast_values: List[ForecastValueSQL] = [
            fv for fv in forecast_values if fv.forecast.site_uuid == site_uuid
        ]

        output_dict[site_uuid] = site_latest_forecast_values

    return output_dict
