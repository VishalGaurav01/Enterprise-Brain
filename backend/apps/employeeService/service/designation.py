from sqlalchemy.orm import Session
from apps.employeeService.model.designation import Designation
from apps.employeeService.schema.designation import DesignationCreate
from apps.shared.responses import DesignationGet
from apps.employeeService.repository import designation as repo
from uuid import UUID
from typing import List, Optional

from apps.authService.schema.auth import UserGet

def create_designation(session: Session, data: DesignationCreate, current_user: UserGet) -> DesignationGet:
    desg = Designation(**data.model_dump())
    desg.created_by = current_user.id
    created = repo.create(session, desg)
    return DesignationGet.model_validate(created)

def get_designation(session: Session, designation_id: UUID) -> Optional[DesignationGet]:
    desg = repo.get_by_id(session, designation_id)
    return DesignationGet.model_validate(desg) if desg else None

def get_all_designations(session: Session, skip: int = 0, limit: int = 100) -> List[DesignationGet]:
    desgs = repo.get_all(session, skip, limit)
    return [DesignationGet.model_validate(d) for d in desgs]

def update_designation(session: Session, designation_id: UUID, data: dict) -> Optional[DesignationGet]:
    updated = repo.update(session, designation_id, data)
    return DesignationGet.model_validate(updated) if updated else None

def delete_designation(session: Session, designation_id: UUID) -> bool:
    return repo.delete(session, designation_id)
