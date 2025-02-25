from pvsite_datamodel.write.user_and_site import (
    change_user_site_group,
    create_site_group,
    create_user,
)


def test_create_user(db_session):
    "Test to create a new user."

    site_group_1 = create_site_group(db_session=db_session)

    user_1 = create_user(
        session=db_session,
        email="test_user@test.org",
        site_group_name=site_group_1.site_group_name,
    )

    assert user_1.email == "test_user@test.org"
    assert user_1.site_group.site_group_name == "test_site_group"
    assert user_1.site_group_uuid == site_group_1.site_group_uuid


# test change user site group
def test_change_user_site_group(db_session):
    """Test the change user site group function
    :param db_session: the database session"""
    site_group = create_site_group(db_session=db_session)
    user = create_user(
        session=db_session, email="test_user@gmail.com", site_group_name=site_group.site_group_name
    )
    site_group2 = create_site_group(db_session=db_session, site_group_name="test_site_group2")
    user, user_site_group = change_user_site_group(
        session=db_session,
        email="test_user@gmail.com",
        site_group_name=site_group2.site_group_name,
    )

    assert user_site_group == site_group2.site_group_name
    assert user == "test_user@gmail.com"
