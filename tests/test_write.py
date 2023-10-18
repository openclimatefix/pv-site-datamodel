"""Test write functions."""

import pandas as pd
import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import GenerationSQL
from pvsite_datamodel.write.generation import insert_generation_values
from pvsite_datamodel.write.user_and_site import (create_user, make_site_group)

class TestInsertGenerationValues:
    """Tests for the insert_generation_values function."""

    def test_inserts_generation_for_existing_site(self, db_session, generation_valid_site):
        """Tests inserts values successfully."""
        df = pd.DataFrame(generation_valid_site)
        insert_generation_values(db_session, df)
        db_session.commit()
        # Check data has been written and exists in table
        assert db_session.query(GenerationSQL).count() == 10

    def test_errors_on_invalid_dataframe(self, engine, generation_invalid_dataframe):
        """Tests function errors on invalid dataframe."""
        df = pd.DataFrame(generation_invalid_dataframe)

        with Session(bind=engine) as session:
            num_rows = session.query(GenerationSQL).count()

            with session.begin_nested():
                with pytest.raises(SQLAlchemyError):
                    insert_generation_values(session, df)
                session.rollback()

            # Make sure nothing was written
            assert session.query(GenerationSQL).count() == num_rows

    def test_inserts_generation_duplicates(self, db_session, generation_valid_site):
        """Tests no duplicates."""
        df = pd.DataFrame(generation_valid_site)
        insert_generation_values(db_session, df)
        db_session.commit()
        # Check data has been written and exists in table
        assert db_session.query(GenerationSQL).count() == 10

        # insert the same values
        insert_generation_values(db_session, df)
        db_session.commit()
        assert db_session.query(GenerationSQL).count() == 10


# # create new site
# def test_create_new_site(db_session):
#     site, message = create_new_site(
#         session=db_session,
#         client_site_id=6932,
#         client_site_name="test_site_name",
#         latitude=1.0,
#         longitude=1.0,
#         capacity_kw=1.0,
#     )

#     assert site.client_site_name == "test_site_name"
#     assert site.ml_id == 1
#     assert site.client_site_id == 6932
#     assert (
#         message
#         == f"Site with client site id {site.client_site_id} and site uuid {site.site_uuid} created successfully"
#     )


# # test for create_new_site to check ml_id increments
# def test_create_new_site_twice(db_session):
#     """Test create new site function for ml_id"""

#     site_1, _ = create_new_site(
#         session=db_session,
#         client_site_id=6932,
#         client_site_name="test_site_name",
#         latitude=1.0,
#         longitude=1.0,
#         capacity_kw=1.0,
#     )

#     site_2, _ = create_new_site(
#         session=db_session,
#         client_site_id=6932,
#         client_site_name="test_site_name",
#         latitude=1.0,
#         longitude=1.0,
#         capacity_kw=1.0,
#     )

#     assert site_1.ml_id == 1
#     assert site_2.ml_id == 2


def test_create_user(db_session):
    "Test to create a new user."

    site_group_1 = make_site_group(db_session=db_session)

    user_1 = create_user(
        session=db_session,
        email="test_user@test.org",
        site_group_name=site_group_1.site_group_name,
    )

    assert user_1.email == "test_user@test.org"
    assert user_1.site_group.site_group_name == "test_site_group"
    assert user_1.site_group_uuid == site_group_1.site_group_uuid