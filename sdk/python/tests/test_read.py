""" Test read functions """

import uuid

from sqlalchemy.orm import Query

from pvsite_datamodel.sqlmodels import SiteSQL, StatusSQL
from pvsite_datamodel.read.site import get_all_sites
from pvsite_datamodel.read.site import get_site_by_uuid
from pvsite_datamodel.read.site import get_site_by_client_site_id
from pvsite_datamodel.read.generation import get_pv_generation_by_site
from pvsite_datamodel.read.status import get_latest_status
from pvsite_datamodel.read.generation import get_pv_generation_by_client

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
        # TODO
        pass

    def test_returns_all_generations_in_datetime_window(self, generations, db_session):
        # TODO
        pass


class TestGetPVGenerationBySite:
    """Tests for the get_pv_generation_by_site function"""

    def test_get_pv_generation_by_site(self, generations, db_session):
        query: Query = db_session.query(SiteSQL)
        site: SiteSQL = query.first()
        generations = get_pv_generation_by_site(
            session=db_session,
            site_uuids=[site.site_uuid]
        )
        assert len(generations) == 10


class TestGetLatestStatus:
    """Tests for the get_latest_status function"""

    def test_gets_latest_status_when_exists(self, statuses, db_session):
        status: StatusSQL = get_latest_status(db_session)

        assert status.message == "Status 3"
