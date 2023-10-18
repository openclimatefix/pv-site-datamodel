"""Test Delete Functions"""

from pvsite_datamodel.sqlmodels import UserSQL, SiteSQL
from pvsite_datamodel.write.user_and_site import (
    make_site_group,
    make_site,
    make_user,
    delete_site,
    delete_user,
    delete_site_group,
)


# test to delete a site
def test_delete_site(db_session):
    """Test to delete a site."""

    site_1 = make_site(db_session=db_session, ml_id=1)

    # todo add site to site group

    site_group = make_site_group(db_session=db_session, site_group_name="test_site_group")
    site_group.sites.append(site_1)

    site_uuid = site_1.site_uuid

    message = delete_site(session=db_session, site_uuid=site_uuid)

    site = db_session.query(SiteSQL).filter(SiteSQL.site_uuid == site_uuid).first()

    assert site is None
    assert message == f"Site with site uuid {site_uuid} deleted successfully"


def test_delete_user(db_session):
    """Test to delete a user."""

    site_group_1 = make_site_group(db_session=db_session)

    user_1 = make_user(
        db_session=db_session,
        email="test_user@ocf.org",
        site_group=site_group_1,
    )

    message = delete_user(session=db_session, email=user_1.email)

    user = db_session.query(UserSQL).filter(UserSQL.email == user_1.email).first()

    assert (
        message
        == f"User with email {user_1.email} and site_group_uuid {user_1.site_group_uuid} deleted successfully"
    )
    assert user is None


def test_delete_site_group(db_session):
    site_group = make_site_group(db_session=db_session, site_group_name="test_site_group")

    message = delete_site_group(session=db_session, site_group_name=site_group.site_group_name)

    assert (
        message
        == f"Site group with name {site_group.site_group_name} and site group uuid {site_group.site_group_uuid} deleted successfully."
    )


def test_delete_site_group_with_users(db_session):
    """Test to delete a site group with users."""

    site_group_1 = make_site_group(db_session=db_session)

    _ = make_user(
        db_session=db_session,
        email="test_user@gmail.com",
        site_group=site_group_1,
    )

    message = delete_site_group(session=db_session, site_group_name=site_group_1.site_group_name)

    assert (
        message
        == f"Site group with name {site_group_1.site_group_name} and site group uuid {site_group_1.site_group_uuid} has users and cannot be deleted."
    )