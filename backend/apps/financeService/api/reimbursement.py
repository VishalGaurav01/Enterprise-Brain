from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from core.database import get_db
from apps.shared.customResponse import custom_response
from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet
from apps.financeService.schema.reimbursement import ReimbursementCreate, ReimbursementUpdate
from apps.shared.responses import ReimbursementGet
from apps.financeService.service import reimbursement as service

router = APIRouter(prefix="/reimbursements", tags=["Reimbursement Management"])


@router.post("/")
def create_endpoint(
    data: ReimbursementCreate,
    session: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_reimbursement(session, data, current_user)
        return custom_response(result, "Reimbursement created successfully", 200)
    except Exception as e:
        return custom_response(None, "Reimbursement creation failed", 500, str(e))


@router.get("/")
def list_endpoint(
    skip: int = 0, limit: int = 100,
    session: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_all_reimbursements(session, skip, limit)
        return custom_response(results, "Reimbursements retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to fetch reimbursements", 500, str(e))


@router.get("/employee/{employee_id}")
def list_by_employee_endpoint(
    employee_id: UUID,
    skip: int = 0, limit: int = 100,
    session: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_reimbursements_by_employee(session, employee_id, skip, limit)
        return custom_response(results, "Employee reimbursements retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to fetch employee reimbursements", 500, str(e))


@router.get("/{id}")
def get_endpoint(
    id: UUID,
    session: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.get_reimbursement_by_id(session, id)
        if not result:
            return custom_response(None, "Reimbursement not found", 404)
        return custom_response(result, "Reimbursement retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to fetch reimbursement", 500, str(e))


@router.patch("/{id}")
def update_endpoint(
    id: UUID,
    data: ReimbursementUpdate,
    session: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.update_reimbursement(session, id, data)
        if not result:
            return custom_response(None, "Reimbursement not found", 404)
        return custom_response(result, "Reimbursement updated successfully", 200)
    except Exception as e:
        return custom_response(None, "Update failed", 500, str(e))


@router.delete("/{id}")
def delete_endpoint(
    id: UUID,
    session: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        service.delete_reimbursement(session, id)
        return custom_response(None, "Reimbursement deleted successfully", 200)
    except Exception as e:
        return custom_response(None, "Deletion failed", 500, str(e))
