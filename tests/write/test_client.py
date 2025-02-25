from pvsite_datamodel.write.client import assign_site_to_client, create_client, edit_client
from pvsite_datamodel.write.user_and_site import create_site, make_fake_site


def test_create_client(db_session):
    """Test to create a new client"""
    client = create_client(session=db_session, client_name="Test Client")

    assert client.client_name == "Test Client"


def test_edit_client(db_session):
    """Test to edit a client"""
    client = create_client(session=db_session, client_name="Test Client")

    client = edit_client(
        session=db_session,
        client_uuid=client.client_uuid,
        client_name="Edited Client",
    )

    assert client.client_name == "Edited Client"


def test_assign_site_to_client(db_session):
    """Test to assign a site to a client"""
    site = make_fake_site(db_session=db_session)
    client = create_client(session=db_session, client_name="Test Client")

    message = assign_site_to_client(db_session, site.site_uuid, client.client_name)

    assert site.client_uuid == client.client_uuid
    assert message == (
        f"Site with site uuid {site.site_uuid} successfully assigned "
        f"to the client {client.client_name}"
    )


# test for create_site to check ml_id duplicates are allowed for separate clients
def test_ml_id_duplicate_for_unique_clients(db_session):
    """Test create sites with duplicate ml_id for different clients"""

    site_1, _ = create_site(
        session=db_session,
        client_site_id=6932,
        client_site_name="test_site_name_1",
        latitude=1.0,
        longitude=1.0,
        capacity_kw=1.0,
        ml_id=1,
    )

    site_2, _ = create_site(
        session=db_session,
        client_site_id=6933,
        client_site_name="test_site_name_2",
        latitude=1.0,
        longitude=1.0,
        capacity_kw=1.0,
        ml_id=1,
    )

    assert site_1.ml_id == 1
    assert site_2.ml_id == 1
