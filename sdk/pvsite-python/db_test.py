import datetime as dt
import unittest as t

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from write import get_or_else_create_datetime_interval
import schema


class TestWrite(t.TestCase):

    def testGetOrElseCreateDatetimeInterval(self):
        engine = sa.create_engine('postgresql+psycopg2://solc:pvdb@localhost/pvsitedevelopment', pool_pre_ping=True)

        with sa_orm.Session(engine) as session:
            # Write new data to postgres
            datetime_interval, written_rows = get_or_else_create_datetime_interval(
                session=session,
                start_time=dt.datetime.now(tz=dt.timezone.utc))
            self.assertTrue(len(written_rows) > 0)

            # Check data has been written and exists in table
            query_result = session \
                .query(schema.DatetimeIntervalSQL) \
                .filter(schema.DatetimeIntervalSQL.datetime_interval_uuid == datetime_interval.datetime_interval_uuid) \
                .first()
            self.assertIsNotNone(query_result)