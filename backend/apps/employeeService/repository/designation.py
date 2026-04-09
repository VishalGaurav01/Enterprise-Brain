from sqlalchemy.orm import Session
from apps.employeeService.model.designation import Designation
from uuid import UUID
from typing import List, Optional

def create(session: Session, designation: Designation) -> Designation:
    session.add(designation)
    session.commit()
    session.refresh(designation)
    return designation

def get_by_id(session: Session, designation_id: UUID) -> Optional[Designation]:
    return session.query(Designation).filter(Designation.id == designation_id).first()

def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Designation]:
    return session.query(Designation).offset(skip).limit(limit).all()

def update(session: Session, designation_id: UUID, data: dict) -> Optional[Designation]:
    desg = get_by_id(session, designation_id)
    if not desg:
        return None
    for key, value in data.items():
        setattr(desg, key, value)
    session.commit()
    session.refresh(desg)
    return desg

def delete(session: Session, designation_id: UUID) -> bool:
    desg = get_by_id(session, designation_id)
    if not desg:
        return False
    session.delete(desg)
    session.commit()
    return True
