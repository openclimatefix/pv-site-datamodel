from pvsite_datamodel import StatusSQL
from pvsite_datamodel.read import get_latest_status


class TestGetLatestStatus:
    """Tests for the get_latest_status function."""

    def test_gets_latest_status_when_exists(self, statuses, db_session):
        status: StatusSQL = get_latest_status(db_session)

        assert status.message == "Status 3"
