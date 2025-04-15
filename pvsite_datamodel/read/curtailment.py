"""Read operations for curtailments."""
from typing import List, Optional
from datetime import date, time
from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import CurtailmentSQL


def get_curtailment_by_uuid(
    session: Session, 
    curtailment_uuid: str
) -> Optional[CurtailmentSQL]:
    """Get curtailment by uuid."""
    return session.query(CurtailmentSQL).filter(
        CurtailmentSQL.curtailment_uuid == curtailment_uuid
    ).first()


def get_curtailments_by_site_uuid(session: Session, site_uuid: str) -> List[CurtailmentSQL]:
    """Get all curtailments for a site."""
    return session.query(CurtailmentSQL).filter(CurtailmentSQL.site_uuid == site_uuid).all()


def get_active_curtailments(
    session: Session,
    site_uuid: str,
    target_date: date,
    target_time: time
) -> List[CurtailmentSQL]:
    """Get curtailments that are active for a given datetime."""
    return session.query(CurtailmentSQL).filter(
        CurtailmentSQL.site_uuid == site_uuid,
        CurtailmentSQL.from_date <= target_date,
        CurtailmentSQL.to_date >= target_date,
        CurtailmentSQL.from_time_utc <= target_time,
        CurtailmentSQL.to_time_utc >= target_time
    ).all()
