"""Test Delete Functions"""

from pvsite_datamodel.sqlmodels import LocationHistorySQL, LocationSQL, UserSQL
from pvsite_datamodel.write.user_and_site import (
    create_site_group,
    create_user,
    delete_site,
    delete_site_group,
    delete_user,
    make_fake_site,
)


# test to delete a site
def test_delete_site(db_session):
    """Test to delete a site."""

    site_1 = make_fake_site(db_session=db_session, ml_id=1)

    # history table should contain a single entry
    hist_size = (
        db_session.query(LocationHistorySQL)
        .filter(LocationHistorySQL.operation_type == "INSERT")
        .count()
    )
    assert hist_size == 1

    # todo add site to site group

    site_group = create_site_group(db_session=db_session, site_group_name="test_site_group")
    site_group.locations.append(site_1)

    site_uuid = site_1.location_uuid

    message = delete_site(session=db_session, site_uuid=site_uuid)

    site = db_session.query(LocationSQL).filter(LocationSQL.location_uuid == site_uuid).first()

    assert site is None
    assert message == f"Location with location uuid {site_uuid} deleted successfully"

    deleted_site = (
        db_session.query(LocationHistorySQL)
        .filter(LocationHistorySQL.operation_type == "DELETE")
        .first()
    )
    assert deleted_site.location_uuid == site_uuid


def test_delete_user(db_session):
    """Test to delete a user."""

    site_group_1 = create_site_group(db_session=db_session)

    user_1 = create_user(
        session=db_session,
        email="test_user@ocf.org",
        site_group_name=site_group_1.location_group_name,
    )

    message = delete_user(session=db_session, email=user_1.email)

    user = db_session.query(UserSQL).filter(UserSQL.email == user_1.email).first()

    assert (
        message == f"User with email {user_1.email} and "
        f"location_group_uuid {user_1.location_group_uuid} deleted successfully"
    )
    assert user is None


def test_delete_site_group(db_session):
    site_group = create_site_group(db_session=db_session, site_group_name="test_site_group")

    message = delete_site_group(session=db_session, site_group_name=site_group.location_group_name)

    assert (
        message == f"Location group with name {site_group.location_group_name} and "
        f"location group uuid {site_group.location_group_uuid} deleted successfully."
    )


def test_delete_site_group_with_users(db_session):
    """Test to delete a site group with users."""

    site_group_1 = create_site_group(db_session=db_session)

    _ = create_user(
        session=db_session,
        email="test_user@gmail.com",
        site_group_name=site_group_1.location_group_name,
    )

    message = delete_site_group(
        session=db_session,
        site_group_name=site_group_1.location_group_name,
    )

    assert (
        message == f"Location group with name {site_group_1.location_group_name} and "
        f"location group uuid {site_group_1.location_group_uuid} has users and cannot be deleted."
    )
