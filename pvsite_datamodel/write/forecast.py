"""
Write helpers for the Forecast and ForecastValues table.
"""

import logging

import pandas as pd
from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL

_log = logging.getLogger(__name__)


def insert_forecast_values(
    session: Session,
    forecast_meta: dict,
    forecast_values_df: pd.DataFrame,
):
    """Insert a dataframe of forecast values and forecast meta info into the database.

    :param session: sqlalchemy session for interacting with the database
    :param forecast_meta: Meta info about the forecast values
    :param forecast_values_df: dataframe with the data to insert
    """

    forecast = ForecastSQL(**forecast_meta)
    session.add(forecast)

    # Flush to get the Forecast's primary key.
    session.flush()

    rows = forecast_values_df.to_dict("records")
    session.bulk_save_objects(
        [
            ForecastValueSQL(
                **row,
                forecast_uuid=forecast.forecast_uuid,
            )
            for row in rows
        ]
    )
    session.commit()
