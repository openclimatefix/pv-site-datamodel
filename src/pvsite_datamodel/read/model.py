"""Read functions for getting ML models."""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL, LocationSQL, MLModelSQL

logger = logging.getLogger(__name__)


def get_or_create_model(
    session: Session,
    name: str,
    version: str | None = None,
    description: str | None = None,
) -> MLModelSQL:
    """Get model object from name and version.

    A new model is made if it doesn't not exists

    :param session: database session
    :param name: name of the model
    :param version: version of the model
    :param description: description of the model

    return: Model object

    """
    # start main query
    query = session.query(MLModelSQL)

    # filter on gsp_id
    query = query.filter(MLModelSQL.name == name)
    if version is not None:
        query = query.filter(MLModelSQL.version == version)

    # gets the latest version
    query = query.order_by(MLModelSQL.version.desc())

    # get all results
    models = query.all()

    if len(models) == 0:
        logger.debug(
            f"Model for name {name} and version {version} does not exist so going to add it",
        )
        model = MLModelSQL(name=name, version=version)

        if description is not None:
            model.description = description
        else:
            # get last model not with this version,
            # so that we can copy the description forward
            last_model = (
                session.query(MLModelSQL)
                .distinct(MLModelSQL.name)
                .filter(MLModelSQL.name == name)
                .order_by(MLModelSQL.name, MLModelSQL.created_utc.desc())
                .one_or_none()
            )
            if last_model is not None:
                model.description = last_model.description

        session.add(model)
        session.commit()

    else:
        model = models[0]

    return model


def get_models(
    session: Session,
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
    site_uuid: str | None = None,
    forecast_horizon: int | None = None,
) -> list[MLModelSQL]:
    """Get model names from forecast values.

    They are distinct on model name
    By adding start and end datetimes, we only look at forecast values in that time range.
    By adding site_uuid, we only look at forecast values for that site.

    :param session: database session
    :param start_datetime: optional filter on start datetime
    :param end_datetime: optional filter on end datetime
    :param site_uuid: optional filter on site uuid
    :return: list of model names
    """
    query = session.query(MLModelSQL)

    query = query.distinct(MLModelSQL.name)

    if (
        (start_datetime is not None)
        or (end_datetime is not None)
        or (site_uuid is not None)
        or (forecast_horizon is not None)
    ):
        query = query.join(ForecastValueSQL)

    if start_datetime is not None:
        query = query.where(ForecastValueSQL.start_utc > start_datetime)

    if end_datetime is not None:
        query = query.where(ForecastValueSQL.start_utc < end_datetime)

    if site_uuid is not None:
        query = query.join(ForecastSQL)
        query = query.join(LocationSQL)
        query = query.where(LocationSQL.location_uuid == site_uuid)

        if start_datetime is not None:
            query = query.where(ForecastSQL.created_utc >= start_datetime)
            query = query.where(ForecastSQL.timestamp_utc >= start_datetime)

        if end_datetime is not None:
            query = query.where(ForecastSQL.created_utc < end_datetime)
            query = query.where(ForecastSQL.timestamp_utc < end_datetime)

    # we can use this to trim the query down,
    # as we only need to check for one forecast_horizon
    if forecast_horizon is not None:
        query = query.where(ForecastValueSQL.horizon_minutes == forecast_horizon)

    # order by created utc desc
    query = query.order_by(MLModelSQL.name, MLModelSQL.created_utc.desc())

    models: [MLModelSQL] = query.all()
    return models
