from sqlalchemy.orm import Session
from apps.employeeService.model.department import Department
from apps.employeeService.schema.department import DepartmentCreate
from apps.shared.responses import DepartmentGet
from apps.employeeService.repository import department as repo
from uuid import UUID
from typing import List, Optional

from apps.authService.schema.auth import UserGet


def create_department(session: Session, data: DepartmentCreate, current_user: UserGet) -> DepartmentGet:
    dept = Department(**data.model_dump())
    dept.created_by = current_user.id
    created = repo.create(session, dept)
    return DepartmentGet.model_validate(created)

def get_department(session: Session, department_id: UUID) -> Optional[DepartmentGet]:
    dept = repo.get_by_id(session, department_id)
    return DepartmentGet.model_validate(dept) if dept else None

def get_all_departments(session: Session, skip: int = 0, limit: int = 100) -> List[DepartmentGet]:
    depts = repo.get_all(session, skip, limit)
    return [DepartmentGet.model_validate(d) for d in depts]

def update_department(session: Session, department_id: UUID, data: dict) -> Optional[DepartmentGet]:
    updated = repo.update(session, department_id, data)
    return DepartmentGet.model_validate(updated) if updated else None

def delete_department(session: Session, department_id: UUID) -> bool:
    return repo.delete(session, department_id)
