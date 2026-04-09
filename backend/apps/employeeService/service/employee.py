from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from apps.authService.schema.auth import UserGet
from uuid import UUID
from typing import Optional, List

from apps.employeeService.model.employee import Employee
from apps.employeeService.schema.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeDelete,
)
from apps.shared.responses import EmployeeGet
from apps.employeeService.repository.employee import (
    create as repo_create,
    get_by_id as repo_get_by_id,
    get_all as repo_get_all,
    update as repo_update,
    delete as repo_delete,
    get_by_email as repo_get_by_email,
    get_by_user_code as repo_get_by_user_code,
)


from apps.shared.kafka_producer import BrainKafkaProducer

# ==================== CREATE Operations ====================
def create_employee(
    session: Session,
    employee_data: EmployeeCreate,
    current_user: UserGet,
) -> EmployeeGet:
    """
    Create a new employee.

    Args:
        session: Database session.
        employee_data: Employee creation data.

    Returns:
        Created employee object.

    Raises:
        ValueError: If employee with same email or code already exists.
        SQLAlchemyError: For database errors.
    """
    try:
        # Check for duplicate email
        existing_email = repo_get_by_email(session, employee_data.email)
        if existing_email:
            raise ValueError(f"Employee with email {employee_data.email} already exists")

        # Check for duplicate user code
        existing_code = repo_get_by_user_code(session, employee_data.user_code)
        if existing_code:
            raise ValueError(f"Employee with code {employee_data.user_code} already exists")

        # Create new employee
        employee = Employee(**employee_data.model_dump())
        employee.created_by = current_user.id
        created_employee = repo_create(session, employee)

        # Publish Kafka Event
        BrainKafkaProducer.publish_event(
            topic="employee-events",
            event_type="EMPLOYEE_CREATED",
            data={"employee_id": str(created_employee.id), "email": created_employee.email}
        )

        return EmployeeGet.model_validate(created_employee)

    except IntegrityError as e:
        session.rollback()
        raise ValueError(f"Integrity error: {str(e.orig)}")
    except SQLAlchemyError as e:
        session.rollback()
        raise SQLAlchemyError(f"Database error: {str(e)}")


# ==================== READ Operations ====================
def get_employee_by_id(
    session: Session,
    employee_id: UUID,
) -> Optional[EmployeeGet]:
    """
    Get employee by ID.

    Args:
        session: Database session.
        employee_id: Employee unique ID.

    Returns:
        Employee object or None if not found.
    """
    try:
        employee = repo_get_by_id(session, employee_id)
        if employee:
            return EmployeeGet.model_validate(employee)
        return None
    except SQLAlchemyError as e:
        raise SQLAlchemyError(f"Database error: {str(e)}")


def get_employee_by_email(
    session: Session,
    email: str,
) -> Optional[EmployeeGet]:
    """
    Get employee by email.

    Args:
        session: Database session.
        email: Employee email.

    Returns:
        Employee object or None if not found.
    """
    try:
        employee = repo_get_by_email(session, email)
        if employee:
            return EmployeeGet.model_validate(employee)
        return None
    except SQLAlchemyError as e:
        raise SQLAlchemyError(f"Database error: {str(e)}")


def get_employee_by_user_code(
    session: Session,
    user_code: str,
) -> Optional[EmployeeGet]:
    """
    Get employee by user code.

    Args:
        session: Database session.
        user_code: Employee user code.

    Returns:
        Employee object or None if not found.
    """
    try:
        employee = repo_get_by_user_code(session, user_code)
        if employee:
            return EmployeeGet.model_validate(employee)
        return None
    except SQLAlchemyError as e:
        raise SQLAlchemyError(f"Database error: {str(e)}")


def get_all_employees(
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[EmployeeGet]:
    """
    Get all employees with pagination.

    Args:
        session: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of employee objects.
    """
    try:
        employees = repo_get_all(session, skip=skip, limit=limit)
        return [EmployeeGet.model_validate(emp) for emp in employees]
    except SQLAlchemyError as e:
        raise SQLAlchemyError(f"Database error: {str(e)}")


# ==================== UPDATE Operations ====================
def update_employee(
    session: Session,
    employee_id: UUID,
    employee_data: EmployeeUpdate,
) -> Optional[EmployeeGet]:
    """
    Update an existing employee.

    Args:
        session: Database session.
        employee_id: Employee unique ID.
        employee_data: Employee update data.

    Returns:
        Updated employee object or None if not found.

    Raises:
        ValueError: If update violates unique constraints.
        SQLAlchemyError: For database errors.
    """
    try:
        # Check if employee exists
        employee = repo_get_by_id(session, employee_id)
        if not employee:
            return None

        # Validate email uniqueness if being updated
        if employee_data.email and employee_data.email != employee.email:
            existing = repo_get_by_email(session, employee_data.email)
            if existing:
                raise ValueError(f"Email {employee_data.email} already in use")

        # Validate user code uniqueness if being updated
        if employee_data.user_code and employee_data.user_code != employee.user_code:
            existing = repo_get_by_user_code(session, employee_data.user_code)
            if existing:
                raise ValueError(f"User code {employee_data.user_code} already in use")

        # Update employee
        update_data = employee_data.model_dump(exclude_unset=True)
        updated_employee = repo_update(session, employee_id, update_data)

        # Publish Kafka Event
        BrainKafkaProducer.publish_event(
            topic="employee-events",
            event_type="EMPLOYEE_UPDATED",
            data={"employee_id": str(updated_employee.id), "fields": list(update_data.keys())}
        )

        return EmployeeGet.model_validate(updated_employee)

    except IntegrityError as e:
        session.rollback()
        raise ValueError(f"Integrity error: {str(e.orig)}")
    except SQLAlchemyError as e:
        session.rollback()
        raise SQLAlchemyError(f"Database error: {str(e)}")


# ==================== DELETE Operations ====================
def delete_employee(
    session: Session,
    employee_id: UUID,
) -> Optional[EmployeeDelete]:
    """
    Delete an employee.

    Args:
        session: Database session.
        employee_id: Employee unique ID.

    Returns:
        Deletion confirmation or None if employee not found.

    Raises:
        SQLAlchemyError: For database errors.
    """
    try:
        # Check if employee exists
        employee = repo_get_by_id(session, employee_id)
        if not employee:
            return None

        # Delete employee
        deleted = repo_delete(session, employee_id)

        return EmployeeDelete(
            id=deleted.id,
            message="Employee deleted successfully"
        )

    except SQLAlchemyError as e:
        session.rollback()
        raise SQLAlchemyError(f"Database error: {str(e)}")
