from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from apps.projectService.model.revenue import ProjectRevenue
from apps.projectService.schema.revenue import ProjectRevenueCreate
from apps.shared.responses import ProjectRevenueGet
from apps.projectService.repository import revenue as repo
from apps.authService.schema.auth import UserGet

def create_revenue(session: Session, data: ProjectRevenueCreate, current_user: UserGet) -> ProjectRevenueGet:
    rev = ProjectRevenue(**data.model_dump())
    rev.created_by = current_user.id
    created = repo.create(session, rev)
    return ProjectRevenueGet.model_validate(created)

def get_all_revenues(session: Session, skip: int = 0, limit: int = 100) -> List[ProjectRevenueGet]:
    revs = repo.get_all(session, skip, limit)
    return [ProjectRevenueGet.model_validate(r) for r in revs]

def get_revenue_by_id(session: Session, rev_id: UUID) -> Optional[ProjectRevenueGet]:
    rev = repo.get_by_id(session, rev_id)
    return ProjectRevenueGet.model_validate(rev) if rev else None

def delete_revenue_record(session: Session, rev_id: UUID) -> bool:
    return repo.delete(session, rev_id)
