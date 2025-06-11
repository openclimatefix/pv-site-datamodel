"""Write operations for curtailments."""
from datetime import date, time
from uuid import UUID
from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import CurtailmentSQL


def create_curtailment(
    session: Session,
    site_uuid: UUID,
    from_date: date,
    to_date: date,
    from_time_utc: time,
    to_time_utc: time,
    curtailment_kw: float,
    created_by: UUID = None
) -> CurtailmentSQL:
    """Create a new curtailment."""
    curtailment = CurtailmentSQL(
        site_uuid=site_uuid,
        from_date=from_date,
        to_date=to_date,
        from_time_utc=from_time_utc,
        to_time_utc=to_time_utc,
        curtailment_kw=curtailment_kw,
        created_by=created_by
    )
    session.add(curtailment)
    session.commit()
    return curtailment


def update_curtailment(
    session: Session,
    curtailment_uuid: UUID,
    from_date: date = None,
    to_date: date = None,
    from_time_utc: time = None,
    to_time_utc: time = None,
    curtailment_kw: float = None
) -> CurtailmentSQL:
    """Update an existing curtailment."""
    curtailment = session.query(CurtailmentSQL).filter(
        CurtailmentSQL.curtailment_uuid == curtailment_uuid
    ).first()
    
    if from_date:
        curtailment.from_date = from_date
    if to_date:
        curtailment.to_date = to_date
    if from_time_utc:
        curtailment.from_time_utc = from_time_utc
    if to_time_utc:
        curtailment.to_time_utc = to_time_utc
    if curtailment_kw:
        curtailment.curtailment_kw = curtailment_kw
        
    session.commit()
    return curtailment


def delete_curtailment(session: Session, curtailment_uuid: UUID) -> None:
    """Delete a curtailment."""
    curtailment = session.query(CurtailmentSQL).filter(
        CurtailmentSQL.curtailment_uuid == curtailment_uuid
    ).first()
    
    session.delete(curtailment)
    session.commit()
