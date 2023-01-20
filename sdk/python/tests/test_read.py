""" Test read functions """

from pvsite_datamodel.read import get_site
import pytest


def test_get_site(sites, db_session):

    site = get_site(session=db_session, client_name="testclient_1", client_id=1)
    assert site.client_site_id == 1


def test_get_site_not_exists(sites, db_session):
    with pytest.raises(Exception):
        _ = get_site(session=db_session, client_name="testclient_100", client_id=1)
