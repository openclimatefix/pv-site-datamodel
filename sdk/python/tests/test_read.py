""" Test read functions """

import datetime as dt
import uuid

from sqlalchemy.orm import Query
from typing import List

from pvsite_datamodel import SiteSQL, StatusSQL, ClientSQL, DatetimeIntervalSQL
from pvsite_datamodel.read import get_all_sites
from pvsite_datamodel.read import get_site_by_uuid
from pvsite_datamodel.read import get_site_by_client_site_id
from pvsite_datamodel.read import get_pv_generation_by_sites
from pvsite_datamodel.read import get_latest_status
from pvsite_datamodel.read import get_pv_generation_by_client
from pvsite_datamodel.read import get_latest_forecast_values_by_site
from pvsite_datamodel.read.utils import filter_query_by_datetime_interval

import pytest


class TestGetAllSites:
    """Tests for the get_all_sites function"""

    def test_returns_all_sites(self, sites, db_session):
        out = get_all_sites(db_session)

        assert len(out) == len(sites)
        assert out[0] == sites[0]


class TestGetSiteByUUID:
    """Tests for the get_site_by_uuid function"""

    def tests_gets_site_for_existing_uuid(self, sites, db_session):
        site = get_site_by_uuid(session=db_session, site_uuid=sites[0].site_uuid)

        assert site == sites[0]

    def test_raises_error_for_nonexistant_site(self, sites, db_session):
        with pytest.raises(Exception):
            _ = get_site_by_uuid(session=db_session, site_uuid=uuid.uuid4())


class TestGetSiteByClientSiteID:
    """Tests for the get_site_by_client_site_id function"""

    def test_gets_site_successfully(self, sites, db_session):
        site = get_site_by_client_site_id(
            session=db_session,
            client_name="testclient_1",
            client_site_id=1
        )

        assert site.client_site_id == 1

    def test_raises_exception_when_no_such_site_exists(self, sites, db_session):
        with pytest.raises(Exception):
            _ = get_site_by_client_site_id(
                session=db_session,
                client_name="testclient_100",
                client_site_id=1
            )


class TestGetPVGenerationByClient:
    """Tests for the get_pv_generation_by_client function"""

    def test_returns_all_generations_without_input_client(self, generations, db_session):
        generations = get_pv_generation_by_client(session=db_session)

        assert len(generations) == 40

    def test_returns_all_generations_for_input_client(self, generations, db_session):
        query: Query = db_session.query(ClientSQL)
        client: ClientSQL = query.first()

        generations = get_pv_generation_by_client(
            session=db_session,
            client_names=[client.client_name]
        )

        assert len(generations) == 10

    def test_returns_all_generations_in_datetime_window(self, generations, db_session):
        query: Query = db_session.query(ClientSQL)
        client: ClientSQL = query.first()
        window_lower: dt.datetime = dt.datetime.today() - dt.timedelta(minutes=7)
        window_upper: dt.datetime = dt.datetime.today() + dt.timedelta(minutes=8)

        generations = get_pv_generation_by_client(
            session=db_session,
            client_names=[client.client_name],
            start_utc=window_lower,
            end_utc=window_upper
        )

        assert len(generations) == 7


class TestGetPVGenerationBySites:
    """Tests for the get_pv_generation_by_sites function"""

    def test_gets_generation_for_single_input_site(self, generations, db_session):
        query: Query = db_session.query(SiteSQL)
        site: SiteSQL = query.first()

        generations = get_pv_generation_by_sites(
            session=db_session,
            site_uuids=[site.site_uuid]
        )

        assert len(generations) == 10
        assert generations[0].datetime_interval is not None
        assert generations[0].site is not None

    def test_gets_generation_for_multiple_input_sites(self, generations, db_session):
        query: Query = db_session.query(SiteSQL)
        sites: List[SiteSQL] = query.all()

        generations = get_pv_generation_by_sites(
            session=db_session,
            site_uuids=[site.site_uuid for site in sites]
        )

        assert len(generations) == 10 * len(sites)

    def test_returns_empty_list_for_no_input_sites(self, generations, db_session):
        generations = get_pv_generation_by_sites(
            session=db_session,
            site_uuids=[]
        )

        assert len(generations) == 0


class TestGetLatestStatus:
    """Tests for the get_latest_status function"""

    def test_gets_latest_status_when_exists(self, statuses, db_session):
        status: StatusSQL = get_latest_status(db_session)

        assert status.message == "Status 3"


class TestGetLatestForecastValuesBySite:
    """Tests for the get_latest_forecast_values_by_site function"""

    def test_gets_latest_forecast_values_with_single_site(self, latestforecastvalues, db_session):
        query: Query = db_session.query(SiteSQL)
        site: SiteSQL = query.first()

        latest_forecast_values = get_latest_forecast_values_by_site(
            session=db_session,
            site_uuids=[site.site_uuid]
        )

        assert len(latest_forecast_values) == 1
        assert len(latest_forecast_values[site.site_uuid]) == 10
        assert latest_forecast_values[site.site_uuid][0].datetime_interval is not None

    def test_gets_latest_forecast_values_with_multiple_sites(
            self, latestforecastvalues, db_session):
        query: Query = db_session.query(SiteSQL)
        sites: SiteSQL = query.all()

        latest_forecast_values = get_latest_forecast_values_by_site(
            session=db_session,
            site_uuids=[site.site_uuid for site in sites]
        )

        assert len(latest_forecast_values) == len(sites)

    def test_gets_latest_forecast_values_filter_start_utc(
            self, latestforecastvalues, db_session):
        query: Query = db_session.query(SiteSQL)
        site: SiteSQL = query.first()

        latest_forecast_values = get_latest_forecast_values_by_site(
            session=db_session,
            site_uuids=[site.site_uuid],
            start_utc=dt.datetime.today() - dt.timedelta(minutes=7)
        )
        assert len(latest_forecast_values[site.site_uuid]) == 7

        latest_forecast_values = get_latest_forecast_values_by_site(
            session=db_session,
            site_uuids=[site.site_uuid],
            start_utc=dt.datetime.today() - dt.timedelta(minutes=5)
        )
        assert len(latest_forecast_values[site.site_uuid]) == 5


class TestFilterQueryByDatetimeInterval:
    """Tests for the filter_query_by_datetime_interval function"""

    def test_returns_datetime_intervals_in_filter(self, datetimeintervals, db_session):
        query: Query = db_session.query(DatetimeIntervalSQL)
        query = filter_query_by_datetime_interval(
            query=query,
            start_utc=dt.datetime.today() - dt.timedelta(minutes=7)
        )

        datetime_intervals: List[DatetimeIntervalSQL] = query.all()

        assert len(datetime_intervals) == 7
