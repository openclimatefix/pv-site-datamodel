"""FastAPI routes for curtailment operations."""
from datetime import date, time
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import CurtailmentSQL
from pvsite_datamodel.read.curtailment import (
    get_curtailment_by_uuid,
    get_curtailments_by_site_uuid,
    get_active_curtailments
)
from pvsite_datamodel.write.curtailment import (
    create_curtailment,
    update_curtailment,
    delete_curtailment
)
from pvsite_datamodel.connection import DatabaseConnection

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = DatabaseConnection().get_session()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CurtailmentSQL)
def create_curtailment_endpoint(
    site_uuid: UUID,
    from_date: date,
    to_date: date,
    from_time: time,
    to_time: time,
    curtailment_kw: float,
    created_by: UUID = None,
    db: Session = Depends(get_db)
):
    """Create a new curtailment."""
    return create_curtailment(
        db,
        site_uuid,
        from_date,
        to_date,
        from_time,
        to_time,
        curtailment_kw,
        created_by
    )

@router.get("/{curtailment_uuid}", response_model=CurtailmentSQL)
def get_curtailment_endpoint(
    curtailment_uuid: UUID,
    db: Session = Depends(get_db)
):
    """Get a curtailment by UUID."""
    curtailment = get_curtailment_by_uuid(db, curtailment_uuid)
    if not curtailment:
        raise HTTPException(status_code=404, detail="Curtailment not found")
    return curtailment

@router.get("/site/{site_uuid}", response_model=List[CurtailmentSQL])
def get_curtailments_for_site_endpoint(
    site_uuid: UUID,
    apply_curtailments: bool = Query(default=True, description="Apply curtailment reductions to forecasts"),
    db: Session = Depends(get_db)
):
    """Get all curtailments for a site.
    
    Args:
        site_uuid: The UUID of the site to get curtailments for
        apply_curtailments: Whether to apply curtailment reductions to forecasts (default: True)
    
    Returns:
        List of curtailments for the specified site
    """
    return get_curtailments_by_site_uuid(db, site_uuid, apply_curtailments)

@router.put("/{curtailment_uuid}", response_model=CurtailmentSQL)
def update_curtailment_endpoint(
    curtailment_uuid: UUID,
    from_date: date = None,
    to_date: date = None,
    from_time: time = None,
    to_time: time = None,
    curtailment_kw: float = None,
    db: Session = Depends(get_db)
):
    """Update a curtailment."""
    return update_curtailment(
        db,
        curtailment_uuid,
        from_date,
        to_date,
        from_time,
        to_time,
        curtailment_kw
    )

@router.delete("/{curtailment_uuid}")
def delete_curtailment_endpoint(
    curtailment_uuid: UUID,
    db: Session = Depends(get_db)
):
    """Delete a curtailment."""
    delete_curtailment(db, curtailment_uuid)
    return {"message": "Curtailment deleted successfully"}
