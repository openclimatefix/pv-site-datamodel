""" Read functions for getting ML models. """
import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import ForecastSQL, ForecastValueSQL, MLModelSQL, SiteSQL

logger = logging.getLogger(__name__)


def get_or_create_model(session: Session, name: str, version: Optional[str] = None) -> MLModelSQL:
    """
    Get model object from name and version.

    A new model is made if it doesn't not exists

    :param session: database session
    :param name: name of the model
    :param version: version of the model

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
            f"Model for name {name} and version {version} does not exist so going to add it"
        )

        model = MLModelSQL(name=name, version=version)
        session.add(model)
        session.commit()

    else:
        model = models[0]

    return model


def get_models(
    session: Session,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    site_uuid: Optional[str] = None,
) -> List[MLModelSQL]:
    """
    Get model names from forecast values.

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

    if (start_datetime is not None) or (end_datetime is not None) or (site_uuid is not None):
        query = query.join(ForecastValueSQL)

    if start_datetime is not None:
        query = query.where(ForecastValueSQL.start_utc > start_datetime)

    if end_datetime is not None:
        query = query.where(ForecastValueSQL.start_utc < end_datetime)

    if site_uuid is not None:
        query = query.join(ForecastSQL)
        query = query.join(SiteSQL)
        query = query.where(SiteSQL.site_uuid == site_uuid)

    models: [MLModelSQL] = query.all()
    return models
