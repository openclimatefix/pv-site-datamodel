""" Test read functions """

from sqlalchemy.orm import Query

from pvsite_datamodel.read.site import get_site, get_all_site, get_site_from_uuid
from pvsite_datamodel.read.generation import get_pv_generation_by_client, get_pv_generation_by_site
from pvsite_datamodel.read.status import get_latest_status
from pvsite_datamodel.sqlmodels import SiteSQL, StatusSQL
import pytest


def test_get_site(sites, db_session):
    site = get_site(session=db_session, client_name="testclient_1", client_id=1)
    assert site.client_site_id == 1


def test_get_site_not_exists(sites, db_session):
    with pytest.raises(Exception):
        _ = get_site(session=db_session, client_name="testclient_100", client_id=1)


def test_get_site_from_uuid(sites, db_session):
    site = get_site_from_uuid(session=db_session, site_uuid=sites[0].site_uuid)
    assert site == sites[0]


def test_get_all_site(sites, db_session):
    sites_read = get_all_site(session=db_session)
    assert len(sites_read) == len(sites)
    assert sites_read[0] == sites[0]


def test_get_pv_generation(generations, db_session):
    generations = get_pv_generation_by_client(session=db_session)
    assert len(generations) == 40

    # TODO need to test     start_utc, end_utc, client_names


def test_get_pv_generation_by_site(generations, db_session):
    query: Query = db_session.query(SiteSQL)
    site: SiteSQL = query.first()
    generations = get_pv_generation_by_site(session=db_session, site_uuids=[site.site_uuid])
    assert len(generations) == 10


def test_get_latest_status(statuses, db_session):
    status: StatusSQL = get_latest_status(db_session)

    assert status.message == "Status 3"
