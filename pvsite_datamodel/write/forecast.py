"""
Write helpers for the Forecast and ForecastValues table.
"""

import logging
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from pvsite_datamodel.read.model import get_or_create_model
from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL

_log = logging.getLogger(__name__)


def insert_forecast_values(
    session: Session,
    forecast_meta: dict,
    forecast_values_df: pd.DataFrame,
    ml_model_name: Optional[str] = None,
    ml_model_version: Optional[str] = None,
):
    """Insert a dataframe of forecast values and forecast meta info into the database.

    :param session: sqlalchemy session for interacting with the database
    :param forecast_meta: Meta info about the forecast values
    :param forecast_values_df: dataframe with the data to insert
    :param ml_model_name: name of the ML model used to generate the forecast
    :param ml_model_version: version of the ML model used to generate the forecast
    """

    if "site_uuid" in forecast_meta and "location_uuid" not in forecast_meta:
        forecast_meta["location_uuid"] = forecast_meta["site_uuid"]
        forecast_meta.pop("site_uuid")

    forecast = ForecastSQL(**forecast_meta)
    session.add(forecast)

    # Flush to get the Forecast's primary key.
    session.flush()

    if (ml_model_name is not None) and (ml_model_version is not None):
        ml_model = get_or_create_model(session, ml_model_name, ml_model_version)
        ml_model_uuid = ml_model.model_uuid
    else:
        ml_model_uuid = None

    rows = forecast_values_df.to_dict("records")
    session.bulk_save_objects(
        [
            ForecastValueSQL(
                **row,
                forecast_uuid=forecast.forecast_uuid,
                ml_model_uuid=ml_model_uuid,
            )
            for row in rows
        ]
    )
    session.commit()
