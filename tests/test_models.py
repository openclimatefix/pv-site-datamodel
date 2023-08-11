from pvsite_datamodel.write.user_and_site import make_site, make_site_group, make_user


def test_one_site_one_user(db_session):
    """
    1. Test that one site with one user works
    """

    site_group = make_site_group(db_session=db_session)
    one_site = make_site(db_session=db_session)
    user = make_user(db_session=db_session, email="test_user@gmail.com", site_group=site_group)

    # add site to site group
    site_group.sites.append(one_site)

    assert len(user.site_group.sites) == 1


def test_two_site_one_user(db_session):
    """
    2. Test that one site with one user works
    """

    site_group = make_site_group(db_session=db_session)
    site_1 = make_site(db_session=db_session, ml_id=1)
    site_2 = make_site(db_session=db_session, ml_id=2)
    user = make_user(db_session=db_session, email="test_user@gmail.com", site_group=site_group)

    # add site to site group
    site_group.sites.append(site_1)
    site_group.sites.append(site_2)

    assert len(user.site_group.sites) == 2


def test_one_site_two_user(db_session):
    """
    3. Test that one site with two users works
    """

    site_group = make_site_group(db_session=db_session)
    site_1 = make_site(db_session=db_session, ml_id=1)
    user_1 = make_user(db_session=db_session, email="test_user_1@gmail.com", site_group=site_group)
    user_2 = make_user(db_session=db_session, email="test_user_2@gmail.com", site_group=site_group)

    # add site to site group
    site_group.sites.append(site_1)

    assert len(user_1.site_group.sites) == 1
    assert len(user_2.site_group.sites) == 1


def test_two_site_two_user(db_session):
    """
    4. Test that has two site with two users
    """

    site_group = make_site_group(db_session=db_session)
    site_1 = make_site(db_session=db_session, ml_id=1)
    site_2 = make_site(db_session=db_session, ml_id=2)
    user_1 = make_user(db_session=db_session, email="test_user_1@gmail.com", site_group=site_group)
    user_2 = make_user(db_session=db_session, email="test_user_2@gmail.com", site_group=site_group)

    # add site to site group
    site_group.sites.append(site_1)
    site_group.sites.append(site_2)

    assert len(user_1.site_group.sites) == 2
    assert len(user_2.site_group.sites) == 2


def test_three_site_two_user_and_ocf_see_everything(db_session):
    """
    5. Test that three site with two user works
    """

    site_group = make_site_group(db_session=db_session)
    site_group_ocf = make_site_group(db_session=db_session, site_group_name="OCF")
    site_1 = make_site(db_session=db_session, ml_id=1)
    site_2 = make_site(db_session=db_session, ml_id=2)
    site_3 = make_site(db_session=db_session, ml_id=3)
    user_1 = make_user(db_session=db_session, email="test_user_1@gmail.com", site_group=site_group)
    user_2 = make_user(db_session=db_session, email="test_user_2@gmail.com", site_group=site_group)
    user_ocf = make_user(
        db_session=db_session, email="test_user_ocf@gmail.com", site_group=site_group_ocf
    )

    # add site to site group
    site_group.sites.append(site_1)
    site_group.sites.append(site_2)
    site_group_ocf.sites.append(site_1)
    site_group_ocf.sites.append(site_2)
    site_group_ocf.sites.append(site_3)

    assert len(user_1.site_group.sites) == 2
    assert len(user_2.site_group.sites) == 2
    assert len(user_ocf.site_group.sites) == 3
