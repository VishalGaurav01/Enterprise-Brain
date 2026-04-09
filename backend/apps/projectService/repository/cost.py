from sqlalchemy.orm import Session, joinedload
from apps.projectService.model.cost import ProjectCost
from uuid import UUID
from typing import List, Optional

def create(session: Session, cost: ProjectCost) -> ProjectCost:
    session.add(cost)
    session.commit()
    session.refresh(cost)
    return cost

def get_by_id(session: Session, cost_id: UUID) -> Optional[ProjectCost]:
    return session.query(ProjectCost).options(
        joinedload(ProjectCost.project),
        joinedload(ProjectCost.vendor)
    ).filter(ProjectCost.id == cost_id).first()

def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[ProjectCost]:
    return session.query(ProjectCost).options(joinedload(ProjectCost.project), joinedload(ProjectCost.vendor)).offset(skip).limit(limit).all()

def get_by_project(session: Session, project_id: UUID) -> List[ProjectCost]:
    return session.query(ProjectCost).options(joinedload(ProjectCost.project), joinedload(ProjectCost.vendor)).filter(ProjectCost.project_id == project_id).all()

def delete(session: Session, cost_id: UUID) -> bool:
    cost = get_by_id(session, cost_id)
    if cost:
        session.delete(cost)
        session.commit()
        return True
    return False
