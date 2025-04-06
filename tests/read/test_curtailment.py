"""Tests for curtailment read operations."""
import pytest
from datetime import date, time
from uuid import uuid4
from pvsite_datamodel.read.curtailment import (
    get_curtailment_by_uuid,
    get_curtailments_by_site_uuid,
    get_active_curtailments
)

def test_get_curtailment_by_uuid(db_session, test_curtailment):
    """Test getting curtailment by UUID."""
    result = get_curtailment_by_uuid(db_session, test_curtailment.curtailment_uuid)
    assert result.curtailment_uuid == test_curtailment.curtailment_uuid

def test_get_curtailments_by_site_uuid(db_session, test_site, test_curtailment):
    """Test getting curtailments by site UUID."""
    curtailments = get_curtailments_by_site_uuid(db_session, test_site.site_uuid)
    assert len(curtailments) == 1
    assert curtailments[0].curtailment_uuid == test_curtailment.curtailment_uuid

def test_get_active_curtailments(db_session, test_curtailment):
    """Test getting active curtailments."""
    target_date = date(2023, 1, 1)
    target_time = time(12, 0)
    active = get_active_curtailments(db_session, test_curtailment.site_uuid, target_date, target_time)
    assert len(active) == 1
