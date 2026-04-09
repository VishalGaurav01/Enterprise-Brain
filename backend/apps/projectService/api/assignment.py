from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from core.database import get_db
from apps.shared.customResponse import custom_response
from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet
from apps.projectService.schema.assignment import AssignmentCreate, AssignmentUpdate
from apps.shared.responses import AssignmentGet
from apps.projectService.service import assignment as service

router = APIRouter(prefix="/assignments", tags=["Project Assignments"])

@router.post("/")
def create_endpoint(
    data: AssignmentCreate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_assignment(session, data, current_user)
        return custom_response(result, "Assignment created successfully", 200)
    except Exception as e:
        return custom_response(None, "Assignment creation failed", 500, str(e))

@router.get("/")
def list_endpoint(
    skip: int = 0, limit: int = 100, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_all_assignments(session, skip, limit)
        return custom_response(results, "Assignments retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to retrieve assignments", 500, str(e))

@router.get("/{id}")
def get_endpoint(
    id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.get_assignment_by_id(session, id)
        if not result:
            return custom_response(None, "Assignment not found", 404)
        return custom_response(result, "Assignment retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Assignment retrieval failed", 500, str(e))

@router.get("/employee/{emp_id}")
def get_by_employee_endpoint(
    emp_id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_assignments_by_employee_id(session, emp_id)
        return custom_response(results, "Employee assignments retrieved", 200)
    except Exception as e:
        return custom_response(None, "Failed to fetch employee assignments", 500, str(e))

@router.patch("/{id}")
def update_endpoint(
    id: UUID, 
    data: AssignmentUpdate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.update_assignment_details(session, id, data)
        if not result:
            return custom_response(None, "Assignment not found", 404)
        return custom_response(result, "Assignment updated successfully", 200)
    except Exception as e:
        return custom_response(None, "Update failed", 500, str(e))

@router.delete("/{id}")
def delete_endpoint(
    id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        success = service.delete_assignment_record(session, id)
        if not success:
            return custom_response(None, "Assignment not found", 404)
        return custom_response(None, "Assignment deleted successfully", 200)
    except Exception as e:
        return custom_response(None, "Deletion failed", 500, str(e))
