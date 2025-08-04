
"""Tests for the site_group module."""

import pytest
from unittest.mock import Mock

from pvsite_datamodel.site_group import (
    select_site_by_uuid,
    select_site_by_client_id,
    get_all_site_uuids,
    get_all_client_site_ids,
    add_all_sites_to_site_group,
    change_user_site_group,
)
from pvsite_datamodel.read.user import validate_email


def test_select_site_by_uuid(mocker):
    """Test selecting a site by UUID."""
    mock_session = Mock()
    mock_site = Mock()
    mock_site.location_uuid = "123e4567-e89b-12d3-a456-426614174000"
    mocker.patch(
        "pvsite_datamodel.site_group.get_site_by_uuid",
        return_value=mock_site,
    )

    site_uuid = select_site_by_uuid(
        mock_session, "123e4567-e89b-12d3-a456-426614174000"
    )

    assert site_uuid == "123e4567-e89b-12d3-a456-426614174000"


def test_select_site_by_uuid_not_found(mocker):
    """Test selecting a site by UUID that does not exist."""
    mock_session = Mock()
    mocker.patch(
        "pvsite_datamodel.site_group.get_site_by_uuid",
        side_effect=Exception("Site not found"),
    )

    with pytest.raises(
        ValueError,
        match="Site with UUID 123e4567-e89b-12d3-a456-426614174000 not found"
    ):
        select_site_by_uuid(mock_session, "123e4567-e89b-12d3-a456-426614174000")


def test_select_site_by_client_id(mocker):
    """Test selecting a site by client site ID."""
    mock_session = Mock()
    mock_site = Mock()
    mock_site.location_uuid = "123e4567-e89b-12d3-a456-426614174000"
    mocker.patch(
        "pvsite_datamodel.site_group.get_site_by_client_id",
        return_value=mock_site,
    )

    site_uuid = select_site_by_client_id(mock_session, "client-123")

    assert site_uuid == "123e4567-e89b-12d3-a456-426614174000"


def test_select_site_by_client_id_not_found(mocker):
    """Test selecting a site by client site ID that does not exist."""
    mock_session = Mock()
    mocker.patch(
        "pvsite_datamodel.site_group.get_site_by_client_id",
        side_effect=Exception("Site not found"),
    )

    with pytest.raises(
        ValueError, match="Site with client ID client-123 not found"
    ):
        select_site_by_client_id(mock_session, "client-123")


def test_get_all_site_uuids(mocker):
    """Test getting all site UUIDs."""
    mock_session = Mock()
    mock_uuids = [
        "123e4567-e89b-12d3-a456-426614174000",
        "223e4567-e89b-12d3-a456-426614174000"
    ]
    mocker.patch(
        "pvsite_datamodel.read.site.get_all_site_uuids",
        return_value=mock_uuids,
    )

    site_uuids = get_all_site_uuids(mock_session)

    assert site_uuids == mock_uuids


def test_get_all_client_site_ids(mocker):
    """Test getting all client site IDs."""
    mock_session = Mock()
    mock_client_ids = ["client-123", "client-456"]
    mocker.patch(
        "pvsite_datamodel.read.site.get_all_client_site_ids",
        return_value=mock_client_ids,
    )

    client_site_ids = get_all_client_site_ids(mock_session)

    assert client_site_ids == mock_client_ids


def test_add_all_sites_to_site_group(mocker):
    """Test adding all sites to a site group."""
    mock_session = Mock()
    mock_site_group = Mock()
    mock_site_group.locations = []
    mocker.patch(
        "pvsite_datamodel.site_group.get_site_group_by_name",
        return_value=mock_site_group,
    )
    mocker.patch(
        "pvsite_datamodel.site_group.get_all_sites",
        return_value=[
            Mock(location_uuid="123e4567-e89b-12d3-a456-426614174000"),
            Mock(location_uuid="223e4567-e89b-12d3-a456-426614174000"),
        ],
    )

    message, sites_added = add_all_sites_to_site_group(mock_session, "ocf")

    assert message == "Added 2 sites to group ocf."
    assert sites_added == [
        "123e4567-e89b-12d3-a456-426614174000",
        "223e4567-e89b-12d3-a456-426614174000"
    ]


def test_add_all_sites_to_site_group_no_new_sites(mocker):
    """Test adding all sites to a site group when no new sites are available."""
    mock_session = Mock()
    mock_site_group = Mock()
    mock_site_group.locations = [
        Mock(location_uuid="123e4567-e89b-12d3-a456-426614174000")
    ]
    mocker.patch(
        "pvsite_datamodel.site_group.get_site_group_by_name",
        return_value=mock_site_group,
    )
    mocker.patch(
        "pvsite_datamodel.site_group.get_all_sites",
        return_value=[
            Mock(location_uuid="123e4567-e89b-12d3-a456-426614174000"),
        ],
    )

    message, sites_added = add_all_sites_to_site_group(mock_session, "ocf")

    assert message == "There are no new sites to be added to ocf."
    assert sites_added == []


def test_change_user_site_group(mocker):
    """Test changing a user's site group."""
    mock_session = Mock()
    mock_user = Mock()
    mock_user.email = "test@example.com"
    mock_user.location_group.location_group_name = "new_site_group"
    mocker.patch(
        "pvsite_datamodel.read.user.get_user_by_email",
        return_value=mock_user,
    )
    mocker.patch(
        "pvsite_datamodel.write.user_and_site.update_user_site_group",
    )

    user_email, user_site_group = change_user_site_group(
        mock_session, "test@example.com", "new_site_group"
    )

    assert user_email == "test@example.com"
    assert user_site_group == "new_site_group"


def test_validate_email():
    """Test email validation function."""
    assert validate_email("test@example.com") is True
    assert validate_email("user.name@domain.co.uk") is True
    assert validate_email("valid+email@test.org") is True
    assert validate_email("invalid-email") is False
    assert validate_email("@domain.com") is False
    assert validate_email("user@") is False
    assert validate_email("user@domain") is False
