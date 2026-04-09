from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from core.database import get_db
from apps.shared.customResponse import custom_response
from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet
from apps.financeService.schema.revenue import ProjectRevenueCreate
from apps.shared.responses import ProjectRevenueGet
from apps.financeService.service import revenue as service

router = APIRouter(prefix="/revenues", tags=["Revenue Tracking"])

@router.post("/")
def create_endpoint(
    data: ProjectRevenueCreate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_revenue(session, data, current_user)
        return custom_response(result, "Revenue recorded successfully", 200)
    except Exception as e:
        return custom_response(None, "Revenue recording failed", 500, str(e))

@router.get("/")
def list_endpoint(
    skip: int = 0, limit: int = 100, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_all_revenues(session, skip, limit)
        return custom_response(results, "Revenues retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to fetch revenues", 500, str(e))

@router.delete("/{id}")
def delete_endpoint(
    id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        service.delete_revenue_record(session, id)
        return custom_response(None, "Revenue record deleted", 200)
    except Exception as e:
        return custom_response(None, "Deletion failed", 500, str(e))
