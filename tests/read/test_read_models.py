""" test get models"""

from pvsite_datamodel.read.model import get_model
from pvsite_datamodel.sqlmodels import MLModelSQL


def test_get_model(db_session):
    model_read_1 = get_model(session=db_session, name="test_name", version="9.9.9")
    model_read_2 = get_model(session=db_session, name="test_name", version="9.9.9")

    assert model_read_1.name == model_read_2.name
    assert model_read_1.version == model_read_2.version

    assert len(db_session.query(MLModelSQL).all()) == 1

    _ = get_model(session=db_session, name="test_name", version="9.9.10")
    assert len(db_session.query(MLModelSQL).all()) == 2
