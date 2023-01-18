"""
Tests
"""

import datetime as dt
import unittest as t

import schema
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import testing.postgresql as test_pg
from write import get_or_else_create_datetime_interval

Postgresql = test_pg.PostgresqlFactory(cache_initialized_db=True)


def tearDownModule():
    """
    Runs at the end of the test suite
    """
    # clear cached database at end of tests
    Postgresql.clear_cache()


class TestGetOrElseCreateDateTimeInterval(t.TestCase):
    """
    Tests for the get_or_else_create_datetime_interval function
    """

    postgresql = Postgresql()
    engine = sa.create_engine(postgresql.url())
    test_time = dt.datetime(2022, 7, 25, 0, 0, 0, 0, dt.timezone.utc)

    @classmethod
    def setUpClass(cls) -> None:
        """
        Runs at start of test case
        """
        schema.Base.metadata.create_all(bind=cls.engine)
        print("Created tables")

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Runs at end of test case.
        """
        cls.postgresql.stop()

    def test1_WritesIntervalWhenNotExist(self):
        """
        Tests that the function writes to the db when the datetime_interval doesn't already exist
        """
        with sa_orm.Session(self.engine) as session:
            datetime_interval, written_rows = get_or_else_create_datetime_interval(
                session=session, start_time=self.test_time
            )
            self.assertTrue(len(written_rows) > 0)

            # Check data has been written and exists in table
            query_result = (
                session.query(schema.DatetimeIntervalSQL)
                .filter(
                    schema.DatetimeIntervalSQL.datetime_interval_uuid
                    == datetime_interval.datetime_interval_uuid
                )
                .first()
            )
            self.assertIsNotNone(query_result)

    def test2_GetsExistingIntervalWhenExists(self):
        """
        Tests the function doesn't write to the database when the datetime_interval already exists
        """
        with sa_orm.Session(self.engine) as session:
            datetime_interval, written_rows = get_or_else_create_datetime_interval(
                session=session, start_time=self.test_time
            )
            self.assertTrue(len(written_rows) == 0)
