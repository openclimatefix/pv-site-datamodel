from pvsite_datamodel.write.user_and_site import create_site_group, create_user, make_fake_site


def test_one_site_one_user(db_session):
    """
    1. Test that one site with one user works
    """

    site_group = create_site_group(db_session=db_session)
    one_site = make_fake_site(db_session=db_session)
    user = create_user(
        session=db_session,
        email="test_user@gmail.com",
        site_group_name=site_group.location_group_name,
    )

    # add site to site group
    site_group.locations.append(one_site)

    assert len(user.location_group.locations) == 1


def test_two_site_one_user(db_session):
    """
    2. Test that one site with one user works
    """

    site_group = create_site_group(db_session=db_session)
    site_1 = make_fake_site(db_session=db_session, ml_id=1)
    site_2 = make_fake_site(db_session=db_session, ml_id=2)
    user = create_user(
        session=db_session,
        email="test_user@gmail.com",
        site_group_name=site_group.location_group_name,
    )

    # add site to site group
    site_group.locations.append(site_1)
    site_group.locations.append(site_2)

    assert len(user.location_group.locations) == 2


def test_one_site_two_user(db_session):
    """
    3. Test that one site with two users works
    """

    site_group = create_site_group(db_session=db_session)
    site_1 = make_fake_site(db_session=db_session, ml_id=1)
    user_1 = create_user(
        session=db_session,
        email="test_user_1@gmail.com",
        site_group_name=site_group.location_group_name,
    )
    user_2 = create_user(
        session=db_session,
        email="test_user_2@gmail.com",
        site_group_name=site_group.location_group_name,
    )

    # add site to site group
    site_group.locations.append(site_1)

    assert len(user_1.location_group.locations) == 1
    assert len(user_2.location_group.locations) == 1


def test_two_site_two_user(db_session):
    """
    4. Test that has two site with two users
    """

    site_group = create_site_group(db_session=db_session)
    site_1 = make_fake_site(db_session=db_session, ml_id=1)
    site_2 = make_fake_site(db_session=db_session, ml_id=2)
    user_1 = create_user(
        session=db_session,
        email="test_user_1@gmail.com",
        site_group_name=site_group.location_group_name,
    )
    user_2 = create_user(
        session=db_session,
        email="test_user_2@gmail.com",
        site_group_name=site_group.location_group_name,
    )

    # add site to site group
    site_group.locations.append(site_1)
    site_group.locations.append(site_2)

    assert len(user_1.location_group.locations) == 2
    assert len(user_2.location_group.locations) == 2


def test_three_site_two_user_and_ocf_see_everything(db_session):
    """
    5. Test that three site with two user works
    """

    site_group = create_site_group(db_session=db_session)
    site_group_ocf = create_site_group(db_session=db_session, site_group_name="OCF")
    site_1 = make_fake_site(db_session=db_session, ml_id=1)
    site_2 = make_fake_site(db_session=db_session, ml_id=2)
    site_3 = make_fake_site(db_session=db_session, ml_id=3)
    user_1 = create_user(
        session=db_session,
        email="test_user_1@gmail.com",
        site_group_name=site_group.location_group_name,
    )
    user_2 = create_user(
        session=db_session,
        email="test_user_2@gmail.com",
        site_group_name=site_group.location_group_name,
    )
    user_ocf = create_user(
        session=db_session,
        email="test_user_ocf@gmail.com",
        site_group_name=site_group_ocf.location_group_name,
    )

    # add site to site group
    site_group.locations.append(site_1)
    site_group.locations.append(site_2)
    site_group_ocf.locations.append(site_1)
    site_group_ocf.locations.append(site_2)
    site_group_ocf.locations.append(site_3)

    assert len(user_1.location_group.locations) == 2
    assert len(user_2.location_group.locations) == 2
    assert len(user_ocf.location_group.locations) == 3
