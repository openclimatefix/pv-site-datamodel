"""Tests for curtailment write operations."""
from datetime import date, time
from uuid import uuid4
import pytest
from pvsite_datamodel.write.curtailment import (
    create_curtailment,
    update_curtailment,
    delete_curtailment
)

def test_create_curtailment(db_session, test_site):
    """Test creating a curtailment."""
    curtailment = create_curtailment(
        db_session,
        site_uuid=test_site.site_uuid,
        from_date=date(2023, 1, 1),
        to_date=date(2023, 1, 2),
        from_time_utc=time(10, 0),
        to_time_utc=time(14, 0),
        curtailment_kw=100.0
    )
    assert curtailment.site_uuid == test_site.site_uuid
    assert curtailment.curtailment_kw == 100.0
    assert curtailment.from_date == date(2023, 1, 1)
    assert db_session.query(type(curtailment)).count() == 1

def test_update_curtailment(db_session, test_curtailment):
    """Test updating a curtailment."""
    updated = update_curtailment(
        db_session,
        test_curtailment.curtailment_uuid,
        curtailment_kw=150.0,
        to_date=date(2023, 1, 3)
    )
    assert updated.curtailment_kw == 150.0
    assert updated.to_date == date(2023, 1, 3)

def test_delete_curtailment(db_session, test_curtailment):
    """Test deleting a curtailment."""
    delete_curtailment(db_session, test_curtailment.curtailment_uuid)
    assert db_session.query(type(test_curtailment)).count() == 0
