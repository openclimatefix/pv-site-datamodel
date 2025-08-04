"""Tests for the details module."""

from unittest.mock import Mock

from pvsite_datamodel.read.details import (
    get_user_details,
    get_site_details,
)


class TestGetUserDetails:
    """Test get_user_details function."""

    def test_get_user_details(self):
        """Test getting user details."""
        # Mock objects
        mock_site1 = Mock()
        mock_site1.location_uuid = "site-uuid-1"
        mock_site1.client_location_id = "client-id-1"

        mock_site2 = Mock()
        mock_site2.location_uuid = "site-uuid-2"
        mock_site2.client_location_id = "client-id-2"

        mock_site_group = Mock()
        mock_site_group.location_group_name = "test-group"
        mock_site_group.locations = [mock_site1, mock_site2]

        mock_user = Mock()
        mock_user.location_group = mock_site_group

        mock_session = Mock()

        # Mock the get_user_by_email function
        import pvsite_datamodel.read.details
        original_get_user_by_email = (
            pvsite_datamodel.read.details.get_user_by_email
        )
        pvsite_datamodel.read.details.get_user_by_email = Mock(
            return_value=mock_user
        )

        try:
            user_sites, user_site_group, user_site_count = get_user_details(
                mock_session, "test@example.com"
            )

            assert user_site_group == "test-group"
            assert user_site_count == 2
            assert len(user_sites) == 2
            assert user_sites[0]["site_uuid"] == "site-uuid-1"
            assert user_sites[0]["client_site_id"] == "client-id-1"
        finally:
            # Restore original function
            pvsite_datamodel.read.details.get_user_by_email = (
                original_get_user_by_email
            )


class TestGetSiteDetails:
    """Test get_site_details function."""

    def test_get_site_details_with_asset_type_enum(self):
        """Test getting site details with LocationAssetType enum."""
        from datetime import datetime
        from pvsite_datamodel.sqlmodels import LocationAssetType

        # Mock site object
        mock_ml_model = Mock()
        mock_ml_model.name = "test-model"

        mock_site = Mock()
        mock_site.location_uuid = "test-uuid"
        mock_site.client_location_id = "test-client-id"
        mock_site.client_location_name = "test-site-name"
        mock_site.location_groups = []
        mock_site.latitude = 51.5
        mock_site.longitude = -0.1
        mock_site.country = "UK"
        mock_site.asset_type = LocationAssetType.pv
        mock_site.region = "London"
        mock_site.dno = "UK Power Networks"
        mock_site.gsp = "LOND"
        mock_site.tilt = 30
        mock_site.orientation = 180
        mock_site.inverter_capacity_kw = 100
        mock_site.module_capacity_kw = 120
        mock_site.capacity_kw = 100
        mock_site.ml_model_uuid = "model-uuid"
        mock_site.ml_model = mock_ml_model
        mock_site.created_utc = datetime(2023, 1, 1)

        mock_session = Mock()

        # Mock the get_site_by_uuid function
        import pvsite_datamodel.read.details
        original_get_site_by_uuid = (
            pvsite_datamodel.read.details.get_site_by_uuid
        )
        pvsite_datamodel.read.details.get_site_by_uuid = Mock(
            return_value=mock_site
        )

        try:
            site_details = get_site_details(mock_session, "test-uuid")

            assert site_details["site_uuid"] == "test-uuid"
            assert site_details["client_site_id"] == "test-client-id"
            assert site_details["asset_type"] == "pv"
            assert site_details["ml_model_name"] == "test-model"
            assert site_details["capacity"] == "100 kw"
        finally:
            # Restore original function
            pvsite_datamodel.read.details.get_site_by_uuid = (
                original_get_site_by_uuid
            )

