"""Tests for curtailment API endpoints."""
import datetime as dt
from uuid import UUID
from fastapi.testclient import TestClient
from pvsite_datamodel.sqlmodels import CurtailmentSQL
from pvsite_datamodel.api.curtailment import router

client = TestClient(router)

def test_get_curtailments_with_application(test_db_session, test_site):
    """Test getting curtailments with application to forecasts."""
    # Create test curtailment
    curtailment = CurtailmentSQL(
        site_uuid=test_site.site_uuid,
        from_date=dt.date(2023, 1, 1),
        to_date=dt.date(2023, 1, 1),
        from_time_utc=dt.time(12, 0),
        to_time_utc=dt.time(14, 0),
        curtailment_kw=50.0
    )
    test_db_session.add(curtailment)
    test_db_session.commit()

    # Test with curtailment application
    response = client.get(
        f"/site/{test_site.site_uuid}",
        params={"apply_curtailments": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["curtailment_kw"] == 50.0

def test_get_curtailments_without_application(test_db_session, test_site):
    """Test getting curtailments without application to forecasts."""
    # Create test curtailment
    curtailment = CurtailmentSQL(
        site_uuid=test_site.site_uuid,
        from_date=dt.date(2023, 1, 1),
        to_date=dt.date(2023, 1, 1),
        from_time_utc=dt.time(12, 0),
        to_time_utc=dt.time(14, 0),
        curtailment_kw=50.0
    )
    test_db_session.add(curtailment)
    test_db_session.commit()

    # Test without curtailment application
    response = client.get(
        f"/site/{test_site.site_uuid}",
        params={"apply_curtailments": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["curtailment_kw"] == 50.0

def test_get_curtailments_invalid_site_uuid():
    """Test getting curtailments with invalid site UUID."""
    invalid_uuid = "invalid-uuid"
    response = client.get(f"/site/{invalid_uuid}")
    assert response.status_code == 422  # Validation error

def test_get_curtailments_non_existent_site(test_db_session):
    """Test getting curtailments for non-existent site."""
    non_existent_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/site/{non_existent_uuid}")
    assert response.status_code == 200
    assert response.json() == []

def test_multiple_curtailments(test_db_session, test_site):
    """Test handling multiple curtailments for a site."""
    # Create multiple curtailments
    for i in range(3):
        curtailment = CurtailmentSQL(
            site_uuid=test_site.site_uuid,
            from_date=dt.date(2023, 1, 1),
            to_date=dt.date(2023, 1, 1),
            from_time_utc=dt.time(12 + i, 0),
            to_time_utc=dt.time(14 + i, 0),
            curtailment_kw=50.0 + i * 10
        )
        test_db_session.add(curtailment)
    test_db_session.commit()

    response = client.get(f"/site/{test_site.site_uuid}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert sorted([c["curtailment_kw"] for c in data]) == [50.0, 60.0, 70.0]

def test_curtailment_application_edge_cases(test_db_session, test_site):
    """Test edge cases for curtailment application."""
    # Create curtailment at midnight
    curtailment = CurtailmentSQL(
        site_uuid=test_site.site_uuid,
        from_date=dt.date(2023, 1, 1),
        to_date=dt.date(2023, 1, 1),
        from_time_utc=dt.time(0, 0),
        to_time_utc=dt.time(1, 0),
        curtailment_kw=50.0
    )
    test_db_session.add(curtailment)
    test_db_session.commit()

    response = client.get(
        f"/site/{test_site.site_uuid}",
        params={"apply_curtailments": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["curtailment_kw"] == 50.0
