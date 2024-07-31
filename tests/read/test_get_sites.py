import uuid

import pytest

from pvsite_datamodel import SiteGroupSQL
from pvsite_datamodel.pydantic_models import LatitudeLongitudeLimits
from pvsite_datamodel.read import (
    get_all_site_groups,
    get_all_sites,
    get_all_users,
    get_site_by_client_site_id,
    get_site_by_client_site_name,
    get_site_by_uuid,
    get_site_group_by_name,
    get_sites_by_country,
    get_sites_from_user,
)


class TestGetAllSites:
    """Tests for the get_all_sites function."""

    def test_returns_all_sites(self, sites, db_session):
        out = get_all_sites(db_session)

        assert len(out) == len(sites)

        site = [s for s in sites if s.site_uuid == out[0].site_uuid][0]
        assert out[0] == site

        # check uuid is in order
        assert out[1].site_uuid > out[0].site_uuid
        assert out[2].site_uuid > out[1].site_uuid
        assert out[3].site_uuid > out[2].site_uuid

        # check uuid is in order
        assert out[1].site_uuid > out[0].site_uuid
        assert out[2].site_uuid > out[1].site_uuid
        assert out[3].site_uuid > out[2].site_uuid


class TestGetSitesByCountry:
    """Tests for the get_sites_by_country function."""

    def test_returns_correct_uk_sites(self, make_sites_for_country, db_session):
        country = "uk"
        sites = make_sites_for_country(country)
        out = get_sites_by_country(db_session, country)

        assert len(out) == len(sites)
        assert all([o.country == country for o in out])

    def test_returns_correct_india_sites(self, make_sites_for_country, db_session):
        country = "india"
        sites = make_sites_for_country(country)
        out = get_sites_by_country(db_session, country)

        assert len(out) == len(sites)
        assert all([o.country == country for o in out])

    def test_returns_correct_client_name(self, make_sites_for_country, db_session):
        country = "india"
        sites = make_sites_for_country(country)
        out = get_sites_by_country(db_session, country, client_name="test")
        assert len(out) == len(sites)

        out = get_sites_by_country(db_session, country, client_name="test2")
        assert len(out) == 0

    def test_returns_no_sites_for_unknown_country(self, make_sites_for_country, db_session):
        _ = make_sites_for_country("uk")
        out = get_sites_by_country(db_session, "nocountry")

        assert len(out) == 0


class TestGetSiteByUUID:
    """Tests for the get_site_by_uuid function."""

    def tests_gets_site_for_existing_uuid(self, sites, db_session):
        site = get_site_by_uuid(session=db_session, site_uuid=sites[0].site_uuid)

        assert site == sites[0]

    def test_raises_error_for_nonexistant_site(self, sites, db_session):
        with pytest.raises(KeyError):
            _ = get_site_by_uuid(session=db_session, site_uuid=uuid.uuid4())

    def test_get_site_by_client_site_id(self, sites, db_session):
        site = get_site_by_client_site_id(
            session=db_session,
            client_name=sites[0].client_site_name,
            client_site_id=sites[0].client_site_id,
        )

        assert site == sites[0]

    def test_get_site_by_client_site_name(self, sites, db_session):
        site = get_site_by_client_site_name(
            session=db_session,
            client_name="test_client",
            client_site_name=sites[0].client_site_name,
        )

        assert site == sites[0]


def test_get_site_group_by_name(db_session):
    site_group = SiteGroupSQL(site_group_name="test")
    db_session.add(site_group)
    db_session.commit()

    result = get_site_group_by_name(db_session, "test")

    assert result == site_group


def test_get_site_group_by_name_new_group(db_session):
    _ = get_site_group_by_name(db_session, "test")

    assert len(db_session.query(SiteGroupSQL).all()) == 1


def test_get_all_users(db_session):
    users = get_all_users(session=db_session)
    # assert
    assert len(users) == 0


def test_get_all_site_groups(db_session):
    site_groups = get_all_site_groups(session=db_session)
    # assert
    assert len(site_groups) == 0


def test_get_site_from_user(db_session, user_with_sites):
    sites = get_sites_from_user(session=db_session, user=user_with_sites)
    assert len(sites) > 0


def test_get_site_list_max(db_session, user_with_sites):
    # examples sites are at 51,3
    lat_lon = LatitudeLongitudeLimits(latitude_max=50, longitude_max=4)
    sites = get_sites_from_user(session=db_session, user=user_with_sites, lat_lon_limits=lat_lon)
    assert len(sites) == 0

    lat_lon = LatitudeLongitudeLimits(latitude_max=52, longitude_max=2)
    sites = get_sites_from_user(session=db_session, user=user_with_sites, lat_lon_limits=lat_lon)
    assert len(sites) == 0

    lat_lon = LatitudeLongitudeLimits(latitude_max=52, longitude_max=4)
    sites = get_sites_from_user(session=db_session, user=user_with_sites, lat_lon_limits=lat_lon)
    assert len(sites) > 0


def test_get_site_list_min(db_session, user_with_sites):
    # examples sites are at 51,3
    lat_lon = LatitudeLongitudeLimits(latitude_min=52, longitude_min=2)
    sites = get_sites_from_user(session=db_session, user=user_with_sites, lat_lon_limits=lat_lon)
    assert len(sites) == 0

    lat_lon = LatitudeLongitudeLimits(latitude_min=50, longitude_min=4)
    sites = get_sites_from_user(session=db_session, user=user_with_sites, lat_lon_limits=lat_lon)
    assert len(sites) == 0

    lat_lon = LatitudeLongitudeLimits(latitude_min=50, longitude_min=2)
    sites = get_sites_from_user(session=db_session, user=user_with_sites, lat_lon_limits=lat_lon)
    assert len(sites) > 0
