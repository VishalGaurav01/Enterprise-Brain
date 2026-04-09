from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from core.database import get_db
from apps.shared.customResponse import custom_response
from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet
from apps.projectService.schema.cost import ProjectCostCreate, ProjectCostUpdate
from apps.shared.responses import ProjectCostGet
from apps.projectService.service import cost as service

router = APIRouter(prefix="/costs", tags=["Project Cost Tracking"])

@router.post("/")
def create_endpoint(
    data: ProjectCostCreate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_cost(session, data, current_user)
        return custom_response(result, "Cost recorded successfully", 200)
    except Exception as e:
        return custom_response(None, "Cost recording failed", 500, str(e))

@router.get("/")
def list_endpoint(
    skip: int = 0, limit: int = 100, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_all_costs(session, skip, limit)
        return custom_response(results, "Costs retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to retrieve costs", 500, str(e))

@router.get("/project/{prj_id}")
def project_costs_endpoint(
    prj_id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_costs_by_project_id(session, prj_id)
        return custom_response(results, "Project costs retrieved", 200)
    except Exception as e:
        return custom_response(None, "Failed to fetch project costs", 500, str(e))

@router.delete("/{id}")
def delete_endpoint(
    id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        service.delete_cost_record(session, id)
        return custom_response(None, "Cost record deleted", 200)
    except Exception as e:
        return custom_response(None, "Deletion failed", 500, str(e))
