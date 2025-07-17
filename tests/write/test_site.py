import uuid

import pytest

from pvsite_datamodel.pydantic_models import PVSiteEditMetadata
from pvsite_datamodel.read.user import get_user_by_email
from pvsite_datamodel.sqlmodels import LocationHistorySQL
from pvsite_datamodel.write.user_and_site import (
    add_child_location_to_parent_location,
    add_site_to_site_group,
    assign_model_name_to_site,
    create_site,
    create_site_group,
    edit_site,
    make_fake_site,
    remove_site_from_site_group,
    set_site_to_inactive_if_not_in_site_group,
)


# create new site, this will be one in a different issue
def test_create_new_site(db_session):
    site, message = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_name",
        latitude=51.0,
        longitude=0.0,
        capacity_kw=1.0,
    )

    assert site.client_location_name == "test_site_name"
    assert site.ml_id == 1
    assert site.client_location_id == 6932
    assert site.country == "uk"
    assert (
        message == f"Site with client location id {site.client_location_id} "
        f"and location uuid {site.location_uuid} created successfully"
    )


def test_create_new_site_with_user(db_session):
    user = get_user_by_email(session=db_session, email="test@test.com")

    site, message = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_1",
        latitude=51.0,
        longitude=0.0,
        capacity_kw=1.0,
        user_uuid=user.user_uuid,
    )

    # after creating there should be an entry in the history table
    h_site = (
        db_session.query(LocationHistorySQL)
        .filter(LocationHistorySQL.operation_type == "INSERT")
        .first()
    )

    assert h_site.location_uuid == site.location_uuid
    assert h_site.changed_by == user.user_uuid

    # create site without setting user
    site_2, _ = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_2",
        latitude=51.0,
        longitude=0.0,
        capacity_kw=1.0,
    )

    h_site_2 = (
        db_session.query(LocationHistorySQL)
        .filter(LocationHistorySQL.location_uuid == site_2.location_uuid)
        .first()
    )

    # user should not be set
    assert h_site_2.changed_by is None


def test_create_new_site_in_specified_country(db_session):
    site, message = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_name",
        latitude=51.0,
        longitude=0.0,
        capacity_kw=1.0,
        country="india",
    )

    assert site.country == "india"
    assert (
        message == f"Site with client location id {site.client_location_id} "
        f"and location uuid {site.location_uuid} created successfully"
    )


def test_edit_site(db_session):
    """Test the update of site metadata"""
    # history table should be empty
    hist_size = db_session.query(LocationHistorySQL).count()
    assert hist_size == 0

    site = make_fake_site(db_session=db_session)

    # history table should contain a single entry
    hist_size = db_session.query(LocationHistorySQL).count()
    assert hist_size == 1

    prev_latitude = site.latitude

    metadata_to_update = PVSiteEditMetadata(tilt=15, capacity_kw=None)

    user = get_user_by_email(session=db_session, email="test@test.com")
    site, _ = edit_site(
        session=db_session,
        site_uuid=str(site.location_uuid),
        site_info=metadata_to_update,
        user_uuid=user.user_uuid,
    )

    assert site.tilt == metadata_to_update.tilt
    assert site.capacity_kw == metadata_to_update.capacity_kw
    assert site.latitude == prev_latitude

    # after editing there should be another entry in the history table
    hist_size = db_session.query(LocationHistorySQL).count()
    assert hist_size == 2
    h_site = (
        db_session.query(LocationHistorySQL)
        .filter(LocationHistorySQL.operation_type == "UPDATE")
        .first()
    )

    assert h_site.location_uuid == site.location_uuid
    assert h_site.changed_by == user.user_uuid


def test_assign_model_name_to_site(db_session):
    """Test to assign a model name to a site"""
    site = make_fake_site(db_session=db_session)

    assign_model_name_to_site(db_session, site.location_uuid, "test_model")

    assert site.ml_model.name == "test_model"

    assign_model_name_to_site(db_session, site.location_uuid, "test_model_2")

    assert site.ml_model.name == "test_model_2"


def test_assign_model_to_nonexistent_site(db_session):
    """Test assigning a model to a nonexistent site"""
    nonexistent_site_uuid = str(uuid.uuid4())

    with pytest.raises(
        KeyError,
        match=f"Location uuid {nonexistent_site_uuid} not found in locations table",
    ):
        assign_model_name_to_site(db_session, nonexistent_site_uuid, "test_model")


# add site to site group
def test_add_site_to_site_group(db_session):
    site_group = create_site_group(db_session=db_session)
    site_1 = make_fake_site(db_session=db_session, ml_id=1)
    site_2 = make_fake_site(db_session=db_session, ml_id=2)
    site_3 = make_fake_site(db_session=db_session, ml_id=3)
    site_group.locations.append(site_1)
    site_group.locations.append(site_2)

    add_site_to_site_group(
        session=db_session,
        site_uuid=str(site_3.location_uuid),
        site_group_name=site_group.location_group_name,
    )

    assert len(site_group.locations) == 3


def test_remove_site_from_site_group(db_session):
    site_group = create_site_group(db_session=db_session)
    site_1 = make_fake_site(db_session=db_session, ml_id=1)
    site_2 = make_fake_site(db_session=db_session, ml_id=2)
    site_3 = make_fake_site(db_session=db_session, ml_id=3)
    site_group.locations.append(site_1)
    site_group.locations.append(site_2)

    add_site_to_site_group(
        session=db_session,
        site_uuid=str(site_3.location_uuid),
        site_group_name=site_group.location_group_name,
    )

    assert len(site_group.locations) == 3

    remove_site_from_site_group(
        session=db_session,
        site_uuid=str(site_2.location_uuid),
        site_group_name=site_group.location_group_name,
    )

    assert len(site_group.locations) == 2


# test for create_new_site to check ml_id increments
def test_create_new_site_twice(db_session):
    """Test create new site function for ml_id"""

    site_1, _ = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_name",
        latitude=1.0,
        longitude=1.0,
        capacity_kw=1.0,
    )

    site_2, _ = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_name",
        latitude=1.0,
        longitude=1.0,
        capacity_kw=1.0,
    )

    assert site_1.ml_id == 1
    assert site_2.ml_id == 2


def test_create_new_site_with_invalid_asset_type(db_session):
    with pytest.raises(ValueError, match=r"^Invalid asset_type.*"):
        site, message = create_site(
            session=db_session,
            client_site_id=6932,
            client_site_name="test_site_name",
            latitude=51.0,
            longitude=0.0,
            capacity_kw=1.0,
            asset_type="invalid-asset",
        )


def test_set_to_inactive_if_not_in_site_group(db_session):
    """Test site is set to inactive if user is not in site group"""
    site = make_fake_site(db_session=db_session, ml_id=1)
    user = get_user_by_email(session=db_session, email="test@test.com")

    set_site_to_inactive_if_not_in_site_group(
        session=db_session,
        site_uuid=str(site.location_uuid),
        user_uuid=str(user.user_uuid),
    )

    assert not site.active


def test_set_to_inactive_if_in_two_site_group(db_session):
    """Test site is not set to inactive if user is in two site groups"""
    site_group_1 = create_site_group(db_session=db_session)
    site = make_fake_site(db_session=db_session, ml_id=1)
    site_group_1.locations.append(site)
    user = get_user_by_email(session=db_session, email="test@test.com")

    set_site_to_inactive_if_not_in_site_group(
        session=db_session,
        site_uuid=str(site.location_uuid),
        user_uuid=str(user.user_uuid),
    )

    assert site.active


def test_set_to_inactive_if_in_two_site_group_but_ocf(db_session):
    """Test site is set to inactive if user is in two site groups but one group is OCF"""
    site_group_1 = create_site_group(db_session=db_session, site_group_name="ocf")
    site = make_fake_site(db_session=db_session, ml_id=1)
    site_group_1.locations.append(site)
    user = get_user_by_email(session=db_session, email="test@test.com")

    set_site_to_inactive_if_not_in_site_group(
        session=db_session,
        site_uuid=str(site.location_uuid),
        user_uuid=str(user.user_uuid),
    )

    assert not site.active


def test_add_single_child_location_to_parent_location(db_session):
    location_child = make_fake_site(db_session=db_session, ml_id=1)
    location_parent = make_fake_site(db_session=db_session, ml_id=1)

    assert len(location_child.child_locations) == 0
    assert len(location_child.parent_locations) == 0
    assert len(location_parent.child_locations) == 0
    assert len(location_parent.parent_locations) == 0

    add_child_location_to_parent_location(
        session=db_session,
        child_location_uuid=location_child.location_uuid,
        parent_location_uuid=location_parent.location_uuid,
    )

    assert len(location_child.child_locations) == 0
    assert len(location_child.parent_locations) == 1
    assert len(location_parent.child_locations) == 1
    assert len(location_parent.parent_locations) == 0


def test_add_multiple_child_location_to_parent_location(db_session):
    location_child_1 = make_fake_site(db_session=db_session, ml_id=1)
    location_child_2 = make_fake_site(db_session=db_session, ml_id=1)
    location_parent_1 = make_fake_site(db_session=db_session, ml_id=1)
    location_parent_2 = make_fake_site(db_session=db_session, ml_id=1)

    assert len(location_child_1.child_locations) == 0
    assert len(location_child_1.parent_locations) == 0
    assert len(location_child_2.child_locations) == 0
    assert len(location_child_2.parent_locations) == 0
    assert len(location_parent_1.child_locations) == 0
    assert len(location_parent_1.parent_locations) == 0
    assert len(location_parent_2.child_locations) == 0
    assert len(location_parent_2.parent_locations) == 0

    # add child 1 to parent 1
    add_child_location_to_parent_location(
        session=db_session,
        child_location_uuid=location_child_1.location_uuid,
        parent_location_uuid=location_parent_1.location_uuid,
    )

    assert len(location_child_1.child_locations) == 0
    assert len(location_child_1.parent_locations) == 1
    assert len(location_child_2.child_locations) == 0
    assert len(location_child_2.parent_locations) == 0
    assert len(location_parent_1.child_locations) == 1
    assert len(location_parent_1.parent_locations) == 0
    assert len(location_parent_2.child_locations) == 0
    assert len(location_parent_2.parent_locations) == 0

    # add child 2 to parent 1
    add_child_location_to_parent_location(
        session=db_session,
        child_location_uuid=location_child_2.location_uuid,
        parent_location_uuid=location_parent_1.location_uuid,
    )

    assert len(location_child_1.child_locations) == 0
    assert len(location_child_1.parent_locations) == 1
    assert len(location_child_2.child_locations) == 0
    assert len(location_child_2.parent_locations) == 1
    assert len(location_parent_1.child_locations) == 2
    assert len(location_parent_1.parent_locations) == 0
    assert len(location_parent_2.child_locations) == 0
    assert len(location_parent_2.parent_locations) == 0

    # add child 1 to parent 2
    add_child_location_to_parent_location(
        session=db_session,
        child_location_uuid=location_child_1.location_uuid,
        parent_location_uuid=location_parent_2.location_uuid,
    )

    assert len(location_child_1.child_locations) == 0
    assert len(location_child_1.parent_locations) == 2
    assert len(location_child_2.child_locations) == 0
    assert len(location_child_2.parent_locations) == 1
    assert len(location_parent_1.child_locations) == 2
    assert len(location_parent_1.parent_locations) == 0
    assert len(location_parent_2.child_locations) == 1
    assert len(location_parent_2.parent_locations) == 0
