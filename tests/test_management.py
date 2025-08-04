"""Tests for the management module."""

import pytest
from unittest.mock import Mock

from pvsite_datamodel.management import (
    select_site_by_uuid,
    select_site_by_client_id,
    get_all_site_uuids,
    get_all_client_site_ids,
    add_all_sites_to_site_group,
)
from pvsite_datamodel.read.user import validate_email


class TestSelectSite:
    """Test site selection functions."""

    def test_select_site_by_uuid_success(self):
        """Test successful site selection by UUID."""
        mock_site = Mock()
        mock_site.location_uuid = "test-uuid"

        mock_session = Mock()

        # Mock the get_site_by_uuid function
        import pvsite_datamodel.management
        original_get_site_by_uuid = (
            pvsite_datamodel.management.get_site_by_uuid
        )
        pvsite_datamodel.management.get_site_by_uuid = Mock(
            return_value=mock_site
        )

        try:
            result = select_site_by_uuid(mock_session, "test-uuid")
            assert result == "test-uuid"
        finally:
            # Restore original function
            pvsite_datamodel.management.get_site_by_uuid = (
                original_get_site_by_uuid
            )

    def test_select_site_by_uuid_not_found(self):
        """Test site selection by UUID when site not found."""
        mock_session = Mock()

        # Mock the get_site_by_uuid function to raise exception
        import pvsite_datamodel.management
        original_get_site_by_uuid = (
            pvsite_datamodel.management.get_site_by_uuid
        )
        pvsite_datamodel.management.get_site_by_uuid = Mock(
            side_effect=Exception("Not found")
        )

        try:
            with pytest.raises(
                ValueError, match="Site with UUID test-uuid not found"
            ):
                select_site_by_uuid(mock_session, "test-uuid")
        finally:
            # Restore original function
            pvsite_datamodel.management.get_site_by_uuid = (
                original_get_site_by_uuid
            )

    def test_select_site_by_client_id_success(self):
        """Test successful site selection by client ID."""
        # Mock session and database query
        mock_session = Mock()
        mock_query = Mock()
        mock_site = Mock()
        mock_site.location_uuid = "test-uuid"

        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_site

        result = select_site_by_client_id(mock_session, "client-123")
        assert result == "test-uuid"

    def test_select_site_by_client_id_not_found(self):
        """Test site selection by client ID when site not found."""
        # Mock session and database query to return None (no site found)
        mock_session = Mock()
        mock_query = Mock()

        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # No site found

        with pytest.raises(
            ValueError, match="Site with client ID client-123 not found"
        ):
            select_site_by_client_id(mock_session, "client-123")


class TestGetAllSites:
    """Test functions to get all sites."""

    def test_get_all_site_uuids(self):
        """Test getting all site UUIDs."""
        mock_session = Mock()

        # Mock the underlying function that get_all_site_uuids calls
        import pvsite_datamodel.read.site
        original_get_all_site_uuids = pvsite_datamodel.read.site.get_all_site_uuids
        pvsite_datamodel.read.site.get_all_site_uuids = Mock(
            return_value=["uuid-1", "uuid-2"]
        )

        try:
            result = get_all_site_uuids(mock_session)
            assert result == ["uuid-1", "uuid-2"]
        finally:
            # Restore original function
            pvsite_datamodel.read.site.get_all_site_uuids = original_get_all_site_uuids

    def test_get_all_client_site_ids(self):
        """Test getting all client site IDs."""
        mock_session = Mock()

        # Mock the underlying function that get_all_client_site_ids calls
        import pvsite_datamodel.read.site
        original_get_all_client_site_ids = pvsite_datamodel.read.site.get_all_client_site_ids
        pvsite_datamodel.read.site.get_all_client_site_ids = Mock(
            return_value=["client-1", "client-2"]
        )

        try:
            result = get_all_client_site_ids(mock_session)
            assert result == ["client-1", "client-2"]
        finally:
            # Restore original function
            pvsite_datamodel.read.site.get_all_client_site_ids = original_get_all_client_site_ids


class TestAddAllSitesToSiteGroup:
    """Test adding all sites to a site group."""

    def test_add_all_sites_to_site_group_new_sites(self):
        """Test adding sites when there are new sites to add."""
        # Mock sites
        mock_site1 = Mock()
        mock_site1.location_uuid = "uuid-1"
        mock_site2 = Mock()
        mock_site2.location_uuid = "uuid-2"

        # Mock site group with only one existing site
        mock_existing_site = Mock()
        mock_existing_site.location_uuid = "uuid-1"

        mock_site_group = Mock()
        mock_site_group.locations = [mock_existing_site]

        mock_session = Mock()

        # Mock functions
        import pvsite_datamodel.management
        original_get_all_sites = pvsite_datamodel.management.get_all_sites
        original_get_site_group_by_name = (
            pvsite_datamodel.management.get_site_group_by_name
        )

        pvsite_datamodel.management.get_all_sites = Mock(
            return_value=[mock_site1, mock_site2]
        )
        pvsite_datamodel.management.get_site_group_by_name = Mock(
            return_value=mock_site_group
        )

        try:
            message, sites_added = add_all_sites_to_site_group(
                mock_session, "test-group"
            )

            assert "Added 1 sites to group test-group" in message
            assert sites_added == ["uuid-2"]
            # Verify site2 was added to the group
            assert mock_site2 in mock_site_group.locations
        finally:
            # Restore original functions
            pvsite_datamodel.management.get_all_sites = original_get_all_sites
            pvsite_datamodel.management.get_site_group_by_name = (
                original_get_site_group_by_name
            )


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
