from sqlalchemy.orm import Session, joinedload
from apps.projectService.model.assignment import EmployeeProjectAssignment
from uuid import UUID
from typing import List, Optional

def create(session: Session, assignment: EmployeeProjectAssignment) -> EmployeeProjectAssignment:
    session.add(assignment)
    session.commit()
    session.refresh(assignment)
    return assignment

def get_by_id(session: Session, assignment_id: UUID) -> Optional[EmployeeProjectAssignment]:
    return session.query(EmployeeProjectAssignment).options(
        joinedload(EmployeeProjectAssignment.employee),
        joinedload(EmployeeProjectAssignment.project)
    ).filter(EmployeeProjectAssignment.id == assignment_id).first()

def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[EmployeeProjectAssignment]:
    return session.query(EmployeeProjectAssignment).options(
        joinedload(EmployeeProjectAssignment.employee),
        joinedload(EmployeeProjectAssignment.project)
    ).offset(skip).limit(limit).all()

def get_by_employee(session: Session, employee_id: UUID) -> List[EmployeeProjectAssignment]:
    return session.query(EmployeeProjectAssignment).options(
        joinedload(EmployeeProjectAssignment.employee),
        joinedload(EmployeeProjectAssignment.project)
    ).filter(
        EmployeeProjectAssignment.employee_id == employee_id
    ).all()

def update(session: Session, assignment_id: UUID, data: dict) -> Optional[EmployeeProjectAssignment]:
    assign = get_by_id(session, assignment_id)
    if not assign:
        return None
    for key, value in data.items():
        if hasattr(assign, key):
            setattr(assign, key, value)
    session.commit()
    session.refresh(assign)
    return assign

def delete(session: Session, assignment_id: UUID) -> bool:
    assign = get_by_id(session, assignment_id)
    if assign:
        session.delete(assign)
        session.commit()
        return True
    return False
