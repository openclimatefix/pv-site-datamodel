import datetime as dt

from pvsite_datamodel import APIRequestSQL
from pvsite_datamodel.read import (
    get_all_last_api_request,
    get_api_requests_for_one_user,
    get_user_by_email,
)


def test_get_all_last_api_request(db_session):
    user = get_user_by_email(session=db_session, email="test@test.com")
    db_session.add(APIRequestSQL(user_uuid=user.user_uuid, url="test"))
    db_session.add(APIRequestSQL(user_uuid=user.user_uuid, url="test2"))

    last_requests_sql = get_all_last_api_request(session=db_session)
    assert len(last_requests_sql) == 1
    assert last_requests_sql[0].url == "test2"
    assert last_requests_sql[0].user_uuid == user.user_uuid


def test_get_api_requests_for_one_user(db_session):
    user = get_user_by_email(session=db_session, email="test@test.com")
    db_session.add(APIRequestSQL(user_uuid=user.user_uuid, url="test"))

    requests_sql = get_api_requests_for_one_user(session=db_session, email=user.email)
    assert len(requests_sql) == 1
    assert requests_sql[0].url == "test"


def test_get_api_requests_for_one_user_start_datetime(db_session):
    user = get_user_by_email(session=db_session, email="test@test.com")
    db_session.add(APIRequestSQL(user_uuid=user.user_uuid, url="test"))

    requests_sql = get_api_requests_for_one_user(
        session=db_session,
        email=user.email,
        start_datetime=dt.datetime.now() + dt.timedelta(hours=1),
    )
    assert len(requests_sql) == 0


def test_get_api_requests_for_one_user_end_datetime(db_session):
    user = get_user_by_email(session=db_session, email="test@test.com")
    db_session.add(APIRequestSQL(user_uuid=user.user_uuid, url="test"))

    requests_sql = get_api_requests_for_one_user(
        session=db_session,
        email=user.email,
        end_datetime=dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(hours=1),
    )
    assert len(requests_sql) == 0


def test_get_api_requests_for_one_user_new(db_session):
    user = get_user_by_email(session=db_session, email="test@test.com")
    db_session.add(APIRequestSQL(user_uuid=user.user_uuid, url="test"))

    requests_sql = get_api_requests_for_one_user(
        session=db_session,
        email=user.email,
        include_in_url="API",
        exclude_in_url="UI",
    )
    assert len(requests_sql) == 1
    assert requests_sql[0].url == "test"
