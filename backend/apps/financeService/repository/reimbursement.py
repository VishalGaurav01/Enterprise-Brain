from sqlalchemy.orm import Session, joinedload
from apps.financeService.model.reimbursement import Reimbursement
from uuid import UUID
from typing import List, Optional


def create(session: Session, reimbursement: Reimbursement) -> Reimbursement:
    session.add(reimbursement)
    session.commit()
    session.refresh(reimbursement)
    return reimbursement


def get_by_id(session: Session, reimbursement_id: UUID) -> Optional[Reimbursement]:
    return session.query(Reimbursement).options(
        joinedload(Reimbursement.employee)
    ).filter(Reimbursement.id == reimbursement_id).first()


def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Reimbursement]:
    return session.query(Reimbursement).options(
        joinedload(Reimbursement.employee)
    ).offset(skip).limit(limit).all()


def get_by_employee(session: Session, employee_id: UUID, skip: int = 0, limit: int = 100) -> List[Reimbursement]:
    return session.query(Reimbursement).options(
        joinedload(Reimbursement.employee)
    ).filter(Reimbursement.employee_id == employee_id).offset(skip).limit(limit).all()


def update(session: Session, reimbursement_id: UUID, data: dict) -> Optional[Reimbursement]:
    record = get_by_id(session, reimbursement_id)
    if not record:
        return None
    for key, value in data.items():
        if hasattr(record, key):
            setattr(record, key, value)
    session.commit()
    session.refresh(record)
    return record


def delete(session: Session, reimbursement_id: UUID) -> bool:
    record = get_by_id(session, reimbursement_id)
    if record:
        session.delete(record)
        session.commit()
        return True
    return False
