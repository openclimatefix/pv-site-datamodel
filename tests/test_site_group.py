"""Tests for the site_group module."""

import pytest

from pvsite_datamodel.read.site_group import (
    get_all_client_site_ids,
    get_all_site_uuids,
    select_site_by_client_id,
    select_site_by_uuid,
)
from pvsite_datamodel.write.site_group import (
    add_all_sites_to_site_group,
    update_site_group,
)
from pvsite_datamodel.write.user_and_site import create_site_group, make_fake_site


def test_select_site_by_uuid(db_session):
    """Test selecting a site by UUID."""
    site = make_fake_site(db_session=db_session, ml_id=1)

    result = select_site_by_uuid(db_session, str(site.location_uuid))

    assert result == str(site.location_uuid)


def test_select_site_by_uuid_not_found(db_session):
    """Test selecting a site by UUID that does not exist."""
    with pytest.raises(ValueError, match="Site with UUID .* not found"):
        select_site_by_uuid(db_session, "123e4567-e89b-12d3-a456-426614174000")


def test_select_site_by_client_id(db_session):
    """Test selecting a site by client site ID."""
    site = make_fake_site(db_session=db_session, ml_id=1)

    result = select_site_by_client_id(db_session, str(site.client_location_id))

    assert result == str(site.location_uuid)


def test_select_site_by_client_id_not_found(db_session):
    """Test selecting a site by client site ID that does not exist."""
    with pytest.raises(ValueError, match="Site with client ID .* not found"):
        select_site_by_client_id(db_session, "999999")


def test_get_all_site_uuids(db_session):
    """Test getting all site UUIDs."""
    site1 = make_fake_site(db_session=db_session, ml_id=1)
    site2 = make_fake_site(db_session=db_session, ml_id=2)

    result = get_all_site_uuids(db_session)

    assert str(site1.location_uuid) in result
    assert str(site2.location_uuid) in result


def test_get_all_client_site_ids(db_session):
    """Test getting all client site IDs."""
    site1 = make_fake_site(db_session=db_session, ml_id=1)
    site2 = make_fake_site(db_session=db_session, ml_id=2)

    result = get_all_client_site_ids(db_session)

    assert str(site1.client_location_id) in result
    assert str(site2.client_location_id) in result


def test_add_all_sites_to_site_group(db_session):
    """Test adding all sites to a site group."""
    create_site_group(db_session=db_session, site_group_name="test_group")
    site1 = make_fake_site(db_session=db_session, ml_id=1)
    site2 = make_fake_site(db_session=db_session, ml_id=2)

    message, sites_added = add_all_sites_to_site_group(db_session, "test_group")

    assert "Added 2 sites to group test_group" in message
    assert str(site1.location_uuid) in sites_added
    assert str(site2.location_uuid) in sites_added


def test_add_all_sites_to_site_group_no_new_sites(db_session):
    """Test adding all sites to a site group when no new sites are available."""
    site_group = create_site_group(db_session=db_session, site_group_name="test_group")
    site = make_fake_site(db_session=db_session, ml_id=1)

    # First add the site to the group
    site_group.locations.append(site)
    db_session.commit()

    # Now try to add all sites again
    message, sites_added = add_all_sites_to_site_group(db_session, "test_group")

    assert "There are no new sites to be added to test_group" in message
    assert sites_added == []


def test_update_site_group(db_session):
    """Test updating a site group by adding a site."""
    create_site_group(db_session=db_session, site_group_name="test_group")
    site = make_fake_site(db_session=db_session, ml_id=1)

    result_group, site_group_sites, site_site_groups = update_site_group(
        db_session, str(site.location_uuid), "test_group"
    )

    assert result_group.location_group_name == "test_group"
    assert len(site_group_sites) == 1
    assert site_group_sites[0]["site_uuid"] == str(site.location_uuid)
    assert "test_group" in site_site_groups
