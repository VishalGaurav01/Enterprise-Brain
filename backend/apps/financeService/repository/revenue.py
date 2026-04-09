from sqlalchemy.orm import Session, joinedload
from apps.financeService.model.revenue import ProjectRevenue
from uuid import UUID
from typing import List, Optional

def create(session: Session, revenue: ProjectRevenue) -> ProjectRevenue:
    session.add(revenue)
    session.commit()
    session.refresh(revenue)
    return revenue

def get_by_id(session: Session, rev_id: UUID) -> Optional[ProjectRevenue]:
    return session.query(ProjectRevenue).options(
        joinedload(ProjectRevenue.project),
        joinedload(ProjectRevenue.client),
        joinedload(ProjectRevenue.invoice)
    ).filter(ProjectRevenue.id == rev_id).first()

def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[ProjectRevenue]:
    return session.query(ProjectRevenue).options(
        joinedload(ProjectRevenue.project),
        joinedload(ProjectRevenue.client),
        joinedload(ProjectRevenue.invoice)
    ).offset(skip).limit(limit).all()

def delete(session: Session, rev_id: UUID) -> bool:
    rev = get_by_id(session, rev_id)
    if rev:
        session.delete(rev)
        session.commit()
        return True
    return False
