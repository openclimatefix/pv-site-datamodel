from concurrent.futures import ThreadPoolExecutor
from functools import partial

from pvsite_datamodel.sqlmodels import LocationGroupSQL, UserSQL
from pvsite_datamodel.read import get_user_by_email, validate_email
from pvsite_datamodel.write.user_and_site import create_site_group, create_user


class TestGetUserByEmail:
    """Test for get_user_by_email function"""

    def test_get_user_by_email_no_users_site_group_exists(self, db_session):
        _ = create_site_group(db_session=db_session, site_group_name="site_group_for_test@test.com")
        _ = get_user_by_email(session=db_session, email="test@test.com")
        assert len(db_session.query(UserSQL).all()) == 1
        assert len(db_session.query(LocationGroupSQL).all()) == 1

    def test_get_user_by_email_no_users(self, db_session):
        user = get_user_by_email(session=db_session, email="test@test.com")
        assert user.email == "test@test.com"
        assert len(db_session.query(UserSQL).all()) == 1

    def test_get_user_by_email_with_users(self, db_session):
        site_group = create_site_group(db_session=db_session)
        _ = create_user(
            session=db_session,
            site_group_name=site_group.location_group_name,
            email="test_1@test.com",
        )
        _ = create_user(
            session=db_session,
            site_group_name=site_group.location_group_name,
            email="test_2@test.com",
        )

        user = get_user_by_email(session=db_session, email="test_1@test.com")
        assert user.email == "test_1@test.com"
        assert len(db_session.query(UserSQL).all()) == 2

    def test_get_user_by_email_no_user_maker_user_false(self, db_session):
        user = get_user_by_email(
            session=db_session,
            email="test@test.com",
            make_new_user_if_none=False,
        )
        assert user is None
        assert len(db_session.query(UserSQL).all()) == 0

    def test_make_user_db_twice(self, db_session):
        get_user_by_email_partial = partial(get_user_by_email, db_session, "test@test.com")
        tasks = [get_user_by_email_partial for _ in range(5)]

        with ThreadPoolExecutor() as executor:
            running_tasks = [executor.submit(task) for task in tasks]
            for running_task in running_tasks:
                running_task.result()

        assert len(db_session.query(UserSQL).all()) == 1


class TestValidateEmail:
    """Test email validation function."""

    def test_valid_emails(self):
        """Test valid email addresses."""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name@domain.co.uk") is True
        assert validate_email("valid+email@test.org") is True

    def test_invalid_emails(self):
        """Test invalid email addresses."""
        assert validate_email("invalid-email") is False
        assert validate_email("@domain.com") is False
        assert validate_email("user@") is False
        assert validate_email("user@domain") is False
