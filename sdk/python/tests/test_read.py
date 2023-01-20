""" Test read functions """

from pvsite_datamodel.read import get_site, get_all_site, get_site_from_uuid
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
