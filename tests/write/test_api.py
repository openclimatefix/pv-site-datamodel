from pvsite_datamodel.read.user import get_user_by_email
from pvsite_datamodel.sqlmodels import APIRequestSQL
from pvsite_datamodel.write.database import save_api_call_to_db


def test_save_api_call_to_db(db_session):
    user = get_user_by_email(session=db_session, email="test@test.com")
    url = "test"
    save_api_call_to_db(url=url, session=db_session, user=user)
    assert len(db_session.query(APIRequestSQL).all()) == 1
