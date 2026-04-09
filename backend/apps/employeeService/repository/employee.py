from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from apps.employeeService.model.employee import Employee
from typing import Optional, List
from uuid import UUID


def create(session: Session, employee: Employee) -> Employee:
    """
    Create a new employee.

    Args:
        session: Database session.
        employee: Employee object to be created.

    Returns:
        The created employee object.
    """
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


def get_by_id(session: Session, employee_id: UUID) -> Optional[Employee]:
    """
    Retrieve an employee by their ID.

    Args:
        session: Database session.
        employee_id: The ID of the employee to retrieve.

    Returns:
        The employee object if found, otherwise None.
    """
    result = (
        session.query(Employee)
        .options(
            joinedload(Employee.department),
            joinedload(Employee.designation),
            joinedload(Employee.manager),
            joinedload(Employee.subordinates),
            joinedload(Employee.assignments),
        )
        .filter(Employee.id == employee_id)
        .first()
    )
    return result


def get_by_email(session: Session, email: str) -> Optional[Employee]:
    """
    Retrieve an employee by their email.

    Args:
        session: Database session.
        email: The email of the employee to retrieve.

    Returns:
        The employee object if found, otherwise None.
    """
    result = (
        session.query(Employee)
        .options(
            joinedload(Employee.department),
            joinedload(Employee.designation),
            joinedload(Employee.manager),
            joinedload(Employee.subordinates),
            joinedload(Employee.assignments),
        )
        .filter(Employee.email == email)
        .first()
    )
    return result


def get_by_user_code(session: Session, user_code: str) -> Optional[Employee]:
    """
    Retrieve an employee by their user code.

    Args:
        session: Database session.
        user_code: The user code of the employee to retrieve.

    Returns:
        The employee object if found, otherwise None.
    """
    result = (
        session.query(Employee)
        .options(
            joinedload(Employee.department),
            joinedload(Employee.designation),
            joinedload(Employee.manager),
            joinedload(Employee.subordinates),
            joinedload(Employee.assignments),
        )
        .filter(Employee.user_code == user_code)
        .first()
    )
    return result


def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
    """
    Retrieve all employees with pagination.

    Args:
        session: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        A list of employee objects.
    """
    result = (
        session.query(Employee)
        .options(
            joinedload(Employee.department),
            joinedload(Employee.designation),
            joinedload(Employee.manager),
            joinedload(Employee.subordinates),
            joinedload(Employee.assignments),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    return result


def update(
    session: Session, employee_id: UUID, updated_data: dict
) -> Optional[Employee]:
    """
    Update an existing employee's details.

    Args:
        session: Database session.
        employee_id: The ID of the employee to update.
        updated_data: A dictionary containing the fields to update and their new values.

    Returns:
        The updated employee object if found and updated, otherwise None.
    """
    employee = get_by_id(session, employee_id)
    if not employee:
        return None

    for key, value in updated_data.items():
        if hasattr(employee, key):
            setattr(employee, key, value)

    session.commit()
    session.refresh(employee)
    return employee


def delete(session: Session, employee_id: UUID) -> Optional[Employee]:
    """
    Delete an employee by their ID.

    Args:
        session: Database session.
        employee_id: The ID of the employee to delete.

    Returns:
        The deleted employee object if found, otherwise None.
    """
    employee = get_by_id(session, employee_id)
    if not employee:
        return None

    session.delete(employee)
    session.commit()
    return employee
