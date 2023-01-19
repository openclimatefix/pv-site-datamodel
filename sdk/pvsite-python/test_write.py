"""
Tests
"""

import datetime as dt
import unittest as t
import uuid

import connection
import pandas as pd
import schema
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import testing.postgresql as test_pg
import write

client_uuid = uuid.uuid4()
site_uuid = uuid.uuid4()


def initdb(postgresql):
    """Creates tables in test database according to schema, and writes a site and a client"""
    engine = sa.create_engine(postgresql.url())
    schema.Base.metadata.create_all(bind=engine)
    print("Created tables")
    with sa_orm.Session(engine) as session:
        client = schema.ClientSQL(
            client_uuid=client_uuid,
            client_name="testclient",
            created_utc=dt.datetime.now(dt.timezone.utc),
        )
        site = schema.SiteSQL(
            site_uuid=site_uuid,
            client_uuid=client_uuid,
            client_site_id=1,
            latitude=51,
            longitude=3,
            capacity_kw=4,
            created_utc=dt.datetime.now(dt.timezone.utc),
            updated_utc=dt.datetime.now(dt.timezone.utc),
            ml_id=1,
        )
        session.add(client)
        session.add(site)
        session.commit()


Postgresql = test_pg.PostgresqlFactory(cache_initialized_db=True, on_initialized=initdb)


def tearDownModule():
    """Runs at the end of the test suite"""
    # clear cached database at end of tests
    Postgresql.clear_cache()


class TestConnection(t.TestCase):
    """Tests for the DatabaseConnection object"""

    @classmethod
    def setUpClass(cls) -> None:
        """Runs at start of test case"""
        cls.postgresql = Postgresql()

    @classmethod
    def tearDownClass(cls) -> None:
        """Runs at end of test case."""
        cls.postgresql.stop()

    def testDatabaseConnection(self):
        """Tests it can create a connection without erroring"""
        dbcon = connection.DatabaseConnection(self.postgresql.url(), echo=False)
        session = dbcon.get_session()
        session.query(schema.SiteSQL).first()


class TestGetOrElseCreateDateTimeInterval(t.TestCase):
    """Tests for the get_or_else_create_datetime_interval function"""

    test_time = dt.datetime(2022, 7, 25, 0, 0, 0, 0, dt.timezone.utc)

    @classmethod
    def setUpClass(cls) -> None:
        """Runs at start of test case"""
        cls.postgresql = Postgresql()
        cls.engine = sa.create_engine(cls.postgresql.url())

    @classmethod
    def tearDownClass(cls) -> None:
        """Runs at end of test case."""
        cls.postgresql.stop()

    def test1_WritesIntervalWhenNotExist(self):
        """
        Tests that the function writes to the db when the datetime_interval doesn't already exist.

        Needs to be run after test1 to work.
        """
        with sa_orm.Session(self.engine) as session:
            datetime_interval, written_rows = write.get_or_else_create_datetime_interval(
                session=session, start_time=self.test_time
            )
            self.assertGreater(len(written_rows), 0)

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
        """Tests function doesn't write to db when the datetime_interval already exists"""
        with sa_orm.Session(self.engine) as session:
            datetime_interval, written_rows = write.get_or_else_create_datetime_interval(
                session=session, start_time=self.test_time
            )
            self.assertEqual(0, len(written_rows))


class TestInsertForecastValues(t.TestCase):
    """Tests for the insert_forecast_values function"""

    forecast_validSite = {
        "target_datetime_utc": [
            (dt.datetime.today() - dt.timedelta(minutes=x)).isoformat() for x in range(10)
        ],
        "forecast_kw": [x for x in range(10)],
        "pv_uuid": [site_uuid for x in range(10)],
    }
    forecast_invalidSite = {
        "target_datetime_utc": [dt.datetime.today().isoformat()],
        "forecast_kw": [1],
        "pv_uuid": [uuid.uuid4()],
    }

    @classmethod
    def setUpClass(cls) -> None:
        """Runs at start of test case"""
        cls.postgresql = Postgresql()
        cls.engine = sa.create_engine(cls.postgresql.url())

    @classmethod
    def tearDownClass(cls) -> None:
        """Runs at end of test case."""
        cls.postgresql.stop()

    def test1_InsertsValuesForExistingSite(self):
        """Tests inserts values successfully"""
        with sa_orm.Session(self.engine) as session:
            df = pd.DataFrame(self.forecast_validSite)
            written_rows = write.insert_forecast_values(session=session, df=df)
            self.assertEqual(
                21, len(written_rows)
            )  # 10 datetime intervals, 10 forecast values, 1 forecast

            # Check data has been written and exists in table
            written_forecastvalues = session.query(schema.ForecastValueSQL).all()
            self.assertEqual(10, len(written_forecastvalues))
            written_datetimeintervals = session.query(schema.DatetimeIntervalSQL).all()
            self.assertEqual(10, len(written_datetimeintervals))
            written_forecasts = session.query(schema.ForecastSQL).all()
            self.assertEqual(1, len(written_forecasts))

    def test2_InsertsValuesForExistingSiteAndExistingDatetimeIntervals(self):
        """
        Tests inserts values successfully without creating redundant datetime intervals

        Needs to be run after test1 to work.
        """
        with sa_orm.Session(self.engine) as session:
            # Create DataFrame and write to DB
            df = pd.DataFrame(self.forecast_validSite)
            written_rows = write.insert_forecast_values(session=session, df=df)
            self.assertEqual(11, len(written_rows))  # 10 forecast values, 1 forecast

            # Check correct data has been written and exists in table
            written_forecastvalues = session.query(schema.ForecastValueSQL).all()
            self.assertEqual(20, len(written_forecastvalues))  # 10 more since previous test
            written_datetimeintervals = session.query(schema.DatetimeIntervalSQL).all()
            self.assertEqual(10, len(written_datetimeintervals))  # Unchanged from previous test
            written_forecasts = session.query(schema.ForecastSQL).all()
            self.assertEqual(2, len(written_forecasts))  # 1 more since previous test

    def test3_ErrorsOnInvalidSite(self):
        """Tests function errors when incoming pv_uuid does not exist in sites table"""
        with sa_orm.Session(self.engine) as session:
            df = pd.DataFrame(self.forecast_invalidSite)
            with self.assertRaises(KeyError):
                written_rows = write.insert_forecast_values(session=session, df=df)
                self.assertEqual(len(written_rows), 0)


if __name__ == "__main__":
    t.main()
