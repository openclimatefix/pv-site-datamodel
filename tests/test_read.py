"""Test read functions."""

import datetime as dt
import uuid
from typing import List

import pytest
from sqlalchemy.orm import Query

from pvsite_datamodel import ForecastSQL, ForecastValueSQL, SiteSQL, StatusSQL
from pvsite_datamodel.read import (
    get_all_sites,
    get_latest_forecast_values_by_site,
    get_latest_status,
    get_pv_generation_by_sites,
    get_pv_generation_by_user_uuids,
    get_site_by_uuid,
    get_site_by_client_site_id,
    get_site_by_client_site_name,
)
from pvsite_datamodel.write.user_and_site import make_site_group, make_user


class TestGetAllSites:
    """Tests for the get_all_sites function."""

    def test_returns_all_sites(self, sites, db_session):
        out = get_all_sites(db_session)

        assert len(out) == len(sites)

        assert out[0] == sites[0]


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
            session=db_session, client_name="test_client", client_site_id=1
        )

        assert site == sites[0]

    def test_get_site_by_client_site_name(self, sites, db_session):
        site = get_site_by_client_site_name(
            session=db_session, client_name="test_client", client_site_name="test_site_0"
        )

        assert site == sites[0]


class TestGetPVGenerationByUser:
    """Tests for the get_pv_generation_by_client function."""

    def test_returns_all_generations_without_input_user(self, generations, db_session):
        generations = get_pv_generation_by_user_uuids(session=db_session)

        assert len(generations) == 40

    def test_returns_all_generations_for_input_user(self, generations, db_session):
        # associate site to one user
        site: SiteSQL = db_session.query(SiteSQL).first()
        site_group = make_site_group(db_session=db_session)
        user = make_user(db_session=db_session, site_group=site_group, email="test@test.com")
        site_group.sites.append(site)

        generations = get_pv_generation_by_user_uuids(
            session=db_session, user_uuids=[user.user_uuid]
        )

        assert len(generations) == 10

    def test_returns_all_generations_in_datetime_window(self, generations, db_session):
        # associate site to one user
        site: SiteSQL = db_session.query(SiteSQL).first()
        site_group = make_site_group(db_session=db_session)
        user = make_user(db_session=db_session, site_group=site_group, email="test@test.com")
        site_group.sites.append(site)

        window_lower: dt.datetime = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=7)
        window_upper: dt.datetime = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=8)

        generations = get_pv_generation_by_user_uuids(
            session=db_session,
            user_uuids=[user.user_uuid],
            start_utc=window_lower,
            end_utc=window_upper,
        )

        assert len(generations) == 7


class TestGetPVGenerationBySites:
    """Tests for the get_pv_generation_by_sites function."""

    def test_gets_generation_for_single_input_site(self, generations, db_session):
        query: Query = db_session.query(SiteSQL)
        site: SiteSQL = query.first()

        generations = get_pv_generation_by_sites(session=db_session, site_uuids=[site.site_uuid])

        assert len(generations) == 10
        assert generations[0].start_utc is not None
        assert generations[0].site is not None

    def test_gets_generation_for_multiple_input_sites(self, generations, db_session):
        query: Query = db_session.query(SiteSQL)
        sites: List[SiteSQL] = query.all()

        generations = get_pv_generation_by_sites(
            session=db_session, site_uuids=[site.site_uuid for site in sites]
        )

        assert len(generations) == 10 * len(sites)

    def test_returns_empty_list_for_no_input_sites(self, generations, db_session):
        generations = get_pv_generation_by_sites(session=db_session, site_uuids=[])

        assert len(generations) == 0


class TestGetLatestStatus:
    """Tests for the get_latest_status function."""

    def test_gets_latest_status_when_exists(self, statuses, db_session):
        status: StatusSQL = get_latest_status(db_session)

        assert status.message == "Status 3"


def _add_forecast_value(session, forecast, power: int, ts):
    fv = ForecastValueSQL(
        forecast_uuid=forecast.forecast_uuid,
        forecast_power_kw=power,
        start_utc=ts,
        end_utc=ts + dt.timedelta(minutes=5),
    )
    session.add(fv)


def test_get_latest_forecast_values(db_session, sites):
    site_uuids = [site.site_uuid for site in db_session.query(SiteSQL.site_uuid).limit(2)]

    s1, s2 = site_uuids

    forecast_version = "123"

    # Make sure we have some forecasts in the DB
    s1_f1 = ForecastSQL(
        site_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )
    s1_f2 = ForecastSQL(
        site_uuid=s1,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1, 0, 10),
    )
    s2_f1 = ForecastSQL(
        site_uuid=s2,
        forecast_version=forecast_version,
        timestamp_utc=dt.datetime(2000, 1, 1),
    )

    db_session.add_all([s1_f1, s1_f2, s2_f1])
    db_session.commit()

    d0 = dt.datetime(2000, 1, 1, 0)
    d1 = dt.datetime(2000, 1, 1, 1)
    d2 = dt.datetime(2000, 1, 1, 2)
    d3 = dt.datetime(2000, 1, 1, 3)
    d4 = dt.datetime(2000, 1, 1, 4)

    # site 1 forecast 1
    _add_forecast_value(db_session, s1_f1, 1.0, d0)
    _add_forecast_value(db_session, s1_f1, 2.0, d1)
    _add_forecast_value(db_session, s1_f1, 3.0, d2)

    # site 1 forecast 2
    _add_forecast_value(db_session, s1_f2, 4.0, d2)
    _add_forecast_value(db_session, s1_f2, 5.0, d3)
    _add_forecast_value(db_session, s1_f2, 6.0, d4)

    # Site 2 forecast 1
    _add_forecast_value(db_session, s2_f1, 7.0, d0)
    _add_forecast_value(db_session, s2_f1, 8.0, d1)
    _add_forecast_value(db_session, s2_f1, 9.0, d2)
    db_session.commit()

    latest_forecast = get_latest_forecast_values_by_site(db_session, site_uuids, d1)

    expected = {
        s1: [(d1, 2), (d2, 4), (d3, 5), (d4, 6)],
        s2: [(d1, 8), (d2, 9)],
    }

    assert list(sorted(latest_forecast.keys())) == list(sorted(expected.keys()))

    for site_uuid, forecast_values in latest_forecast.items():
        # Format the values in a way that we can compare them.
        values_as_tuple = [(v.start_utc, v.forecast_power_kw) for v in forecast_values]

        assert values_as_tuple == expected[site_uuid]
