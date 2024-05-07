import datetime as dt
from typing import List

import pytest
from sqlalchemy.orm import Query

from pvsite_datamodel import (
    SiteSQL,
)

from pvsite_datamodel.read import (
    get_pv_generation_by_sites,
    get_pv_generation_by_user_uuids,
)

from pvsite_datamodel.write.user_and_site import create_site_group, create_user


class TestGetPVGenerationByUser:
    """Tests for the get_pv_generation_by_client function."""

    def test_returns_all_generations_without_input_user(self, generations, db_session):
        generations = get_pv_generation_by_user_uuids(session=db_session)

        assert len(generations) == 40

    def test_returns_all_generations_for_input_user(self, generations, db_session):
        # associate site to one user
        site: SiteSQL = db_session.query(SiteSQL).first()
        site_group = create_site_group(db_session=db_session)
        user = create_user(
            session=db_session, site_group_name=site_group.site_group_name, email="test@test.com"
        )
        site_group.sites.append(site)

        generations = get_pv_generation_by_user_uuids(
            session=db_session, user_uuids=[user.user_uuid]
        )

        assert len(generations) == 10

    def test_returns_all_generations_in_datetime_window(self, generations, db_session):
        # associate site to one user
        site: SiteSQL = db_session.query(SiteSQL).first()
        site_group = create_site_group(db_session=db_session)
        user = create_user(
            session=db_session, site_group_name=site_group.site_group_name, email="test@test.com"
        )
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

    def test_gets_generation_for_multiple_sum_total(self, generations, db_session):
        query: Query = db_session.query(SiteSQL)
        sites: List[SiteSQL] = query.all()

        generations = get_pv_generation_by_sites(
            session=db_session, site_uuids=[site.site_uuid for site in sites], sum_by="total"
        )

        assert len(generations) == 10
        assert generations[0].power_kw == 4
        assert generations[1].power_kw == 8
        assert (generations[2].start_utc - generations[1].start_utc).seconds == 60

    def test_gets_generation_for_multiple_sum_gsp(self, generations, db_session):
        query: Query = db_session.query(SiteSQL)
        sites: List[SiteSQL] = query.all()

        generations = get_pv_generation_by_sites(
            session=db_session, site_uuids=[site.site_uuid for site in sites], sum_by="gsp"
        )
        assert len(generations) == 10 * len(sites)

    def test_gets_generation_for_multiple_sum_dno(self, generations, db_session):
        query: Query = db_session.query(SiteSQL)
        sites: List[SiteSQL] = query.all()

        generations = get_pv_generation_by_sites(
            session=db_session, site_uuids=[site.site_uuid for site in sites], sum_by="dno"
        )
        assert len(generations) == 10 * len(sites)

    def test_gets_generation_for_multiple_sum_error(self, generations, db_session):
        query: Query = db_session.query(SiteSQL)
        sites: List[SiteSQL] = query.all()

        with pytest.raises(ValueError):  # noqa
            _ = get_pv_generation_by_sites(
                session=db_session, site_uuids=[site.site_uuid for site in sites], sum_by="blah"
            )
