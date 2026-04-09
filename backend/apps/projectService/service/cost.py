from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from apps.projectService.model.cost import ProjectCost
from apps.projectService.schema.cost import ProjectCostCreate, ProjectCostUpdate
from apps.shared.responses import ProjectCostGet
from apps.projectService.repository import cost as repo
from apps.authService.schema.auth import UserGet

def create_cost(session: Session, data: ProjectCostCreate, current_user: UserGet) -> ProjectCostGet:
    cost = ProjectCost(**data.model_dump())
    cost.created_by = current_user.id
    created = repo.create(session, cost)
    return ProjectCostGet.model_validate(created)

def get_all_costs(session: Session, skip: int = 0, limit: int = 100) -> List[ProjectCostGet]:
    costs = repo.get_all(session, skip, limit)
    return [ProjectCostGet.model_validate(c) for c in costs]

def get_cost_by_id(session: Session, cost_id: UUID) -> Optional[ProjectCostGet]:
    cost = repo.get_by_id(session, cost_id)
    return ProjectCostGet.model_validate(cost) if cost else None

def get_costs_by_project_id(session: Session, prj_id: UUID) -> List[ProjectCostGet]:
    costs = repo.get_by_project(session, prj_id)
    return [ProjectCostGet.model_validate(c) for c in costs]

def delete_cost_record(session: Session, cost_id: UUID) -> bool:
    return repo.delete(session, cost_id)
