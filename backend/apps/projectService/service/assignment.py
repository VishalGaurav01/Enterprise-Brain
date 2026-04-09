from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from apps.projectService.model.assignment import EmployeeProjectAssignment
from apps.projectService.schema.assignment import AssignmentCreate, AssignmentUpdate
from apps.shared.responses import AssignmentGet
from apps.projectService.repository import assignment as repo
from apps.authService.schema.auth import UserGet

from apps.shared.grpc_clients import GrpcClients

def create_assignment(session: Session, data: AssignmentCreate, current_user: UserGet) -> AssignmentGet:
    # Use Case 1: Validate Employee exists via gRPC
    employee = GrpcClients.get_employee(str(data.employee_id))
    if not employee:
        raise ValueError(f"Cannot assign: Employee with ID {data.employee_id} does not exist in Employee Service.")
        
    assign = EmployeeProjectAssignment(**data.model_dump())
    assign.created_by = current_user.id
    created = repo.create(session, assign)
    return AssignmentGet.model_validate(created)

def get_all_assignments(session: Session, skip: int = 0, limit: int = 100) -> List[AssignmentGet]:
    assigns = repo.get_all(session, skip, limit)
    return [AssignmentGet.model_validate(a) for a in assigns]

def get_assignment_by_id(session: Session, assign_id: UUID) -> Optional[AssignmentGet]:
    assign = repo.get_by_id(session, assign_id)
    return AssignmentGet.model_validate(assign) if assign else None

def get_assignments_by_employee_id(session: Session, emp_id: UUID) -> List[AssignmentGet]:
    assigns = repo.get_by_employee(session, emp_id)
    return [AssignmentGet.model_validate(a) for a in assigns]

def update_assignment_details(session: Session, assign_id: UUID, data: AssignmentUpdate) -> Optional[AssignmentGet]:
    updated_data = data.model_dump(exclude_unset=True)
    updated = repo.update(session, assign_id, updated_data)
    return AssignmentGet.model_validate(updated) if updated else None

def delete_assignment_record(session: Session, assign_id: UUID) -> bool:
    return repo.delete(session, assign_id)
