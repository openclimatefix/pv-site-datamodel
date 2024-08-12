""" Read functions for getting ML models. """
import logging
from typing import Optional

from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import MLModelSQL

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
