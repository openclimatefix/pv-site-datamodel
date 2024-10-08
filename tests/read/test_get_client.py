import pytest

from pvsite_datamodel.read import get_client_by_name


class TestGetClientByName:
    """Tests for the get_client_by_name function."""

    def test_get_client_by_name(self, db_session, client):
        client_1 = get_client_by_name(session=db_session, name=client.client_name)
        assert client_1.client_name == "client_name_test"

    def test_create_client_if_nonexistant(self, db_session):
        client_1 = get_client_by_name(
            session=db_session,
            name="Test Nonexistant",
            make_new_client_if_none=True,
        )
        assert client_1.client_name == "Test Nonexistant"

    def test_raises_error_for_nonexistant_client(self, db_session):
        with pytest.raises(Exception, match="Could not find client with name Test Nonexistant"):
            _ = get_client_by_name(
                session=db_session,
                name="Test Nonexistant",
                make_new_client_if_none=False,
            )
