from pvsite_datamodel import DatabaseConnection
from pvsite_datamodel.sqlmodels import LocationSQL


class TestDatabaseConnection:
    """Tests for the DatabaseConnection class."""

    def test_connection(self, engine, sites):
        dbcon = DatabaseConnection(engine.url, echo=False)
        with dbcon.get_session() as session:
            session.query(LocationSQL).first()
