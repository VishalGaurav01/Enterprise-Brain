from sqlalchemy.orm import Session, selectinload
from apps.employeeService.model.department import Department
from uuid import UUID
from typing import List, Optional


def create(session: Session, department: Department) -> Department:
    session.add(department)
    session.commit()
    session.refresh(department)
    return department


def get_by_id(session: Session, department_id: UUID) -> Optional[Department]:
    return (
        session.query(Department)
        .options(selectinload(Department.employees), selectinload(Department.projects))
        .filter(Department.id == department_id)
        .first()
    )


def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Department]:
    return (
        session.query(Department)
        .options(selectinload(Department.employees), selectinload(Department.projects))
        .offset(skip)
        .limit(limit)
        .all()
    )


def update(session: Session, department_id: UUID, data: dict) -> Optional[Department]:
    dept = get_by_id(session, department_id)
    if not dept:
        return None
    for key, value in data.items():
        setattr(dept, key, value)
    session.commit()
    session.refresh(dept)
    return dept


def delete(session: Session, department_id: UUID) -> bool:
    dept = get_by_id(session, department_id)
    if not dept:
        return False
    session.delete(dept)
    session.commit()
    return True
