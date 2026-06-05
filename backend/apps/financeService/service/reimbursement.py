from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from apps.financeService.model.reimbursement import Reimbursement
from apps.financeService.schema.reimbursement import ReimbursementCreate, ReimbursementUpdate
from apps.financeService.repository import reimbursement as repo
from apps.authService.schema.auth import UserGet
from apps.shared.responses import ReimbursementGet


def create_reimbursement(session: Session, data: ReimbursementCreate, current_user: UserGet) -> ReimbursementGet:
    record = Reimbursement(**data.model_dump())
    record.created_by = current_user.id
    created = repo.create(session, record)
    return ReimbursementGet.model_validate(created)


def get_all_reimbursements(session: Session, skip: int = 0, limit: int = 100) -> List[ReimbursementGet]:
    records = repo.get_all(session, skip, limit)
    return [ReimbursementGet.model_validate(r) for r in records]


def get_reimbursement_by_id(session: Session, reimbursement_id: UUID) -> Optional[ReimbursementGet]:
    record = repo.get_by_id(session, reimbursement_id)
    return ReimbursementGet.model_validate(record) if record else None


def get_reimbursements_by_employee(session: Session, employee_id: UUID, skip: int = 0, limit: int = 100) -> List[ReimbursementGet]:
    records = repo.get_by_employee(session, employee_id, skip, limit)
    return [ReimbursementGet.model_validate(r) for r in records]


def update_reimbursement(session: Session, reimbursement_id: UUID, data: ReimbursementUpdate) -> Optional[ReimbursementGet]:
    updated_data = data.model_dump(exclude_unset=True)
    updated = repo.update(session, reimbursement_id, updated_data)
    return ReimbursementGet.model_validate(updated) if updated else None


def delete_reimbursement(session: Session, reimbursement_id: UUID) -> bool:
    return repo.delete(session, reimbursement_id)
