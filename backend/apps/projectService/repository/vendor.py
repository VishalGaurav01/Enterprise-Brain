from sqlalchemy.orm import Session, joinedload
from apps.projectService.model.vendor import Vendor
from uuid import UUID
from typing import List, Optional

def create(session: Session, vendor: Vendor) -> Vendor:
    session.add(vendor)
    session.commit()
    session.refresh(vendor)
    return vendor

def get_by_id(session: Session, vendor_id: UUID) -> Optional[Vendor]:
    return session.query(Vendor).options(joinedload(Vendor.costs)).filter(Vendor.id == vendor_id).first()

def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Vendor]:
    return session.query(Vendor).options(joinedload(Vendor.costs)).offset(skip).limit(limit).all()

def update(session: Session, vendor_id: UUID, data: dict) -> Optional[Vendor]:
    vend = get_by_id(session, vendor_id)
    if not vend:
        return None
    for key, value in data.items():
        if hasattr(vend, key):
            setattr(vend, key, value)
    session.commit()
    session.refresh(vend)
    return vend

def delete(session: Session, vendor_id: UUID) -> bool:
    vend = get_by_id(session, vendor_id)
    if vend:
        session.delete(vend)
        session.commit()
        return True
    return False
