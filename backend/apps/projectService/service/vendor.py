from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from apps.projectService.model.vendor import Vendor
from apps.projectService.schema.vendor import VendorCreate, VendorUpdate
from apps.shared.responses import VendorGet
from apps.projectService.repository import vendor as repo
from apps.authService.schema.auth import UserGet

def create_vendor(session: Session, data: VendorCreate, current_user: UserGet) -> VendorGet:
    vend = Vendor(**data.model_dump())
    vend.created_by = current_user.id
    created = repo.create(session, vend)
    return VendorGet.model_validate(created)

def get_all_vendors(session: Session, skip: int = 0, limit: int = 100) -> List[VendorGet]:
    vends = repo.get_all(session, skip, limit)
    return [VendorGet.model_validate(v) for v in vends]

def get_vendor_by_id(session: Session, vendor_id: UUID) -> Optional[VendorGet]:
    vend = repo.get_by_id(session, vendor_id)
    return VendorGet.model_validate(vend) if vend else None

def update_vendor_details(session: Session, vendor_id: UUID, data: VendorUpdate) -> Optional[VendorGet]:
    updated_data = data.model_dump(exclude_unset=True)
    updated = repo.update(session, vendor_id, updated_data)
    return VendorGet.model_validate(updated) if updated else None

def delete_vendor_record(session: Session, vendor_id: UUID) -> bool:
    return repo.delete(session, vendor_id)
