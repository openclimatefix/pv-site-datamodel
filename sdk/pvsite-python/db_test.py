import datetime as dt
import unittest as t

from sqlalchemy import create_engine
import sqlalchemy.orm as sa_orm
from write import get_or_else_create_datetime_interval


class TestWrite(t.TestCase):

    def testGetOrElseCreateDatetimeInterval(self):
        engine = create_engine('postgresql+psycopg2://solc:pvdb@localhost/pvsitedevelopment', pool_pre_ping=True)

        with sa_orm.Session(engine) as session:
            datetime_interval, created = get_or_else_create_datetime_interval(session=session,
                                                                              start_time=dt.datetime.now(
                                                                                  tz=dt.timezone.utc))
            self.assertTrue(created)

