from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from apps.employeeService.schema.department import DepartmentCreate
from apps.employeeService.service import department as service
from apps.shared.customResponse import custom_response
from uuid import UUID

from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/")
def create_endpoint(
    data: DepartmentCreate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_department(session, data, current_user)
        return custom_response(result, "Department created successfully", 200)
    except Exception as e:
        return custom_response(None, "Department creation failed", 500, str(e))

@router.get("/")
def get_all_endpoint(skip: int = 0, limit: int = 100, session: Session = Depends(get_db)):
    try:
        results = service.get_all_departments(session, skip, limit)
        return custom_response(results, "Departments retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Department retrieval failed", 500, str(e))

@router.get("/{id}")
def get_endpoint(id: UUID, session: Session = Depends(get_db)):
    try:
        result = service.get_department(session, id)
        if not result:
            return custom_response(None, "Department not found", 404)
        return custom_response(result, "Department retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Department retrieval failed", 500, str(e))

@router.patch("/{id}")
def update_endpoint(id: UUID, data: dict, session: Session = Depends(get_db)):
    try:
        result = service.update_department(session, id, data)
        if not result:
            return custom_response(None, "Department not found", 404)
        return custom_response(result, "Department updated successfully", 200)
    except Exception as e:
        return custom_response(None, "Department update failed", 500, str(e))

@router.delete("/{id}")
def delete_endpoint(id: UUID, session: Session = Depends(get_db)):
    try:
        deleted = service.delete_department(session, id)
        if not deleted:
            return custom_response(None, "Department not found", 404)
        return custom_response(None, "Department deleted successfully", 200)
    except Exception as e:
        return custom_response(None, "Department deletion failed", 500, str(e))
