from apps.employeeService.service.employee import (
    create_employee,
    get_all_employees,
    get_employee_by_id,
    update_employee,
    delete_employee,
)
from apps.employeeService.schema.employee import EmployeeCreate
from apps.shared.customResponse import custom_response
from core.database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("/")
def create_employee_endpoint(
    employee_data: EmployeeCreate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    """
    Create a new employee.
    Args:
        employee_data: Employee data
        session: Database session

    Returns:
        Employee created successfully
    """
    try:
        result = create_employee(session, employee_data, current_user)
        return custom_response(result, "Employee created successfully", 200)
    except Exception as e:
        return custom_response(None, "Employee creation failed", 500, str(e))


@router.get("/")
def get_all_endpoint(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_db)
):
    try:
        results = get_all_employees(session, skip, limit)
        return custom_response(results, "Employees retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Employee retrieval failed", 500, str(e))


@router.get("/{id}")
def get_endpoint(id: UUID, session: Session = Depends(get_db)):
    try:
        result = get_employee_by_id(session, id)
        if not result:
            return custom_response(None, "Employee not found", 404)
        return custom_response(result, "Employee retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Employee retrieval failed", 500, str(e))


@router.patch("/{id}")
def update_endpoint(id: UUID, data: dict, session: Session = Depends(get_db)):
    try:
        result = update_employee(session, id, data)
        if not result:
            return custom_response(None, "Employee not found", 404)
        return custom_response(result, "Employee updated successfully", 200)
    except Exception as e:
        return custom_response(None, "Employee update failed", 500, str(e))


@router.delete("/{id}")
def delete_endpoint(id: UUID, session: Session = Depends(get_db)):
    try:
        deleted = delete_employee(session, id)
        if not deleted:
            return custom_response(None, "Employee not found", 404)
        return custom_response(None, "Employee deleted successfully", 200)
    except Exception as e:
        return custom_response(None, "Employee deletion failed", 500, str(e))
