"""Get the latest forecast values."""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Union
import uuid
from uuid import UUID

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from pvsite_datamodel.pydantic_models import ForecastValueSum
from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL, MLModelSQL, SiteSQL

def get_latest_forecast_values_by_site(
    session: Session,
    site_uuids: Union[UUID, List[UUID]],
    start_utc: datetime,
    end_utc: Optional[datetime] = None,
    forecast_horizon_minutes: Optional[int] = None,
    day_ahead_hours: Optional[int] = None,
    day_ahead_timezone_delta_hours: Optional[float] = 0,
    model_name: Optional[str] = None,
) -> Union[Dict[uuid.UUID, List[ForecastValueSQL]], List[ForecastValueSum]]:
    """Get the forecast values by input sites, get the latest value.

    Args:
        session: database session used for querying the database.
        site_uuids: the uuids of the sites that you want forecasts for
        start_utc: start time in UTC for forecast values
        end_utc: end time in UTC for forecast values
        forecast_horizon_minutes: only include forecasts with horizon <= this many minutes
        day_ahead_hours: only include forecasts made at least this many hours ahead
        day_ahead_timezone_delta_hours: timezone offset hours for day-ahead calculations
        model_name: filter forecasts to only include those from this ML model

    Returns:
        Dict mapping site uuids to list of forecast values
    """
    # convert uuid to list if it's a single uuid
    if isinstance(site_uuids, UUID):
        site_uuids = [site_uuids]

    if not site_uuids:
        raise ValueError("No site uuids provided")

    # Check sites exist
    site_query = session.query(SiteSQL).filter(SiteSQL.site_uuid.in_(site_uuids))
    sites = site_query.all()
    if len(sites) != len(site_uuids):
        found_site_uuids = {site.site_uuid for site in sites}
        missing_site_uuids = set(site_uuids) - found_site_uuids
        raise ValueError(f"Sites with UUIDs {missing_site_uuids} not found")

    # If end_utc is not provided, set it to start_utc + 24h
    if end_utc is None:
        end_utc = start_utc + timedelta(hours=24)

    if start_utc >= end_utc:
        raise ValueError("start_utc must be before end_utc")

    if day_ahead_timezone_delta_hours is not None:
        # we use mintues and sql cant handle .5 hours (or any decimals)
        day_ahead_timezone_delta_minute = int(day_ahead_timezone_delta_hours * 60)
    else:
        day_ahead_timezone_delta_minute = None

    # Get subquery for latest forecast for each target datetime
    subquery = (
        session.query(
            ForecastValueSQL.target_datetime_utc,
            func.max(ForecastSQL.creation_datetime_utc).label("latest_creation"),
        )
        .join(ForecastSQL)
        .filter(ForecastValueSQL.target_datetime_utc >= start_utc)
        .filter(ForecastValueSQL.target_datetime_utc < end_utc)
    )

    # Filter by model if specified
    if model_name:
        subquery = subquery.join(
            MLModelSQL, ForecastSQL.ml_model_uuid == MLModelSQL.ml_model_uuid
        )
        subquery = subquery.filter(MLModelSQL.name == model_name)

    # Filter by forecast horizon if specified
    if forecast_horizon_minutes is not None:
        subquery = subquery.filter(
            ForecastValueSQL.target_datetime_utc
            <= ForecastSQL.creation_datetime_utc + timedelta(minutes=forecast_horizon_minutes)
        )

    # Filter by day-ahead if specified
    if day_ahead_hours is not None:
        cutoff_time = timedelta(hours=day_ahead_hours)
        if day_ahead_timezone_delta_minute:
            cutoff_time += timedelta(minutes=day_ahead_timezone_delta_minute)
        subquery = subquery.filter(
            ForecastValueSQL.target_datetime_utc
            >= ForecastSQL.creation_datetime_utc + cutoff_time
        )

    subquery = subquery.group_by(ForecastValueSQL.target_datetime_utc).subquery()

    # Main query to get forecast values
    query = session.query(ForecastValueSQL)
    query = query.join(ForecastSQL)
    query = query.filter(ForecastSQL.site_uuid.in_(site_uuids))

    # Apply filters from subquery
    query = query.join(
        subquery,
        (ForecastValueSQL.target_datetime_utc == subquery.c.target_datetime_utc)
        & (ForecastSQL.creation_datetime_utc == subquery.c.latest_creation),
    )

    # Execute query and get results
    forecast_values = query.all()

    if not forecast_values:
        # Return empty dict with site UUIDs as keys
        return {site_uuid: [] for site_uuid in site_uuids}
    else:
        # Group results by site UUID
        output_dict = {}

        for site_uuid in site_uuids:
            site_latest_forecast_values: List[ForecastValueSQL] = [
                fv for fv in forecast_values 
                if fv.forecast.site_uuid == site_uuid
            ]
            output_dict[site_uuid] = site_latest_forecast_values

        return output_dict
