from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from core.database import get_db
from apps.shared.customResponse import custom_response
from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet
from apps.employeeService.schema.software_tool import SoftwareToolCreate, SoftwareToolUpdate
from apps.shared.responses import SoftwareToolGet
from apps.employeeService.service import software_tool as service

router = APIRouter(prefix="/software-tools", tags=["Software Tool Management"])


@router.post("/")
def create_endpoint(
    data: SoftwareToolCreate,
    session: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_software_tool(session, data, current_user)
        return custom_response(result, "Software tool created successfully", 200)
    except Exception as e:
        return custom_response(None, "Software tool creation failed", 500, str(e))


@router.get("/")
def list_endpoint(
    skip: int = 0, limit: int = 100,
    session: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_all_software_tools(session, skip, limit)
        return custom_response(results, "Software tools retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to fetch software tools", 500, str(e))


@router.get("/department/{department_id}")
def list_by_department_endpoint(
    department_id: UUID,
    skip: int = 0, limit: int = 100,
    session: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_tools_by_department(session, department_id, skip, limit)
        return custom_response(results, "Department software tools retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to fetch department software tools", 500, str(e))


@router.get("/{id}")
def get_endpoint(
    id: UUID,
    session: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.get_software_tool_by_id(session, id)
        if not result:
            return custom_response(None, "Software tool not found", 404)
        return custom_response(result, "Software tool retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to fetch software tool", 500, str(e))


@router.patch("/{id}")
def update_endpoint(
    id: UUID,
    data: SoftwareToolUpdate,
    session: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.update_software_tool(session, id, data)
        if not result:
            return custom_response(None, "Software tool not found", 404)
        return custom_response(result, "Software tool updated successfully", 200)
    except Exception as e:
        return custom_response(None, "Update failed", 500, str(e))


@router.delete("/{id}")
def delete_endpoint(
    id: UUID,
    session: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        service.delete_software_tool(session, id)
        return custom_response(None, "Software tool deleted successfully", 200)
    except Exception as e:
        return custom_response(None, "Deletion failed", 500, str(e))
