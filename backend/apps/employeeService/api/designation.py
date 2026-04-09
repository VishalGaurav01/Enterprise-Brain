from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from apps.employeeService.schema.designation import DesignationCreate
from apps.employeeService.service import designation as service
from apps.shared.customResponse import custom_response
from uuid import UUID

from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet

router = APIRouter(prefix="/designations", tags=["Designations"])

@router.post("/")
def create_endpoint(
    data: DesignationCreate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_designation(session, data, current_user)
        return custom_response(result, "Designation created successfully", 200)
    except Exception as e:
        return custom_response(None, "Designation creation failed", 500, str(e))

@router.get("/")
def get_all_endpoint(skip: int = 0, limit: int = 100, session: Session = Depends(get_db)):
    try:
        results = service.get_all_designations(session, skip, limit)
        return custom_response(results, "Designations retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Designation retrieval failed", 500, str(e))

@router.get("/{id}")
def get_endpoint(id: UUID, session: Session = Depends(get_db)):
    try:
        result = service.get_designation(session, id)
        if not result:
            return custom_response(None, "Designation not found", 404)
        return custom_response(result, "Designation retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Designation retrieval failed", 500, str(e))

@router.patch("/{id}")
def update_endpoint(id: UUID, data: dict, session: Session = Depends(get_db)):
    try:
        result = service.update_designation(session, id, data)
        if not result:
            return custom_response(None, "Designation not found", 404)
        return custom_response(result, "Designation updated successfully", 200)
    except Exception as e:
        return custom_response(None, "Designation update failed", 500, str(e))

@router.delete("/{id}")
def delete_endpoint(id: UUID, session: Session = Depends(get_db)):
    try:
        deleted = service.delete_designation(session, id)
        if not deleted:
            return custom_response(None, "Designation not found", 404)
        return custom_response(None, "Designation deleted successfully", 200)
    except Exception as e:
        return custom_response(None, "Designation deletion failed", 500, str(e))
