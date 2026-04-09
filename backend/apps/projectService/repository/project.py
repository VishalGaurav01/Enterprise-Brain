from sqlalchemy.orm import Session, joinedload
from apps.projectService.model.project import Project
from uuid import UUID
from typing import List, Optional

def create(session: Session, project: Project) -> Project:
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

def get_by_id(session: Session, project_id: UUID) -> Optional[Project]:
    return (
        session.query(Project)
        .options(
            joinedload(Project.department),
            joinedload(Project.owner),
            joinedload(Project.assignments),
            joinedload(Project.costs),
            joinedload(Project.revenues),
            joinedload(Project.client),
            joinedload(Project.invoices),
        )
        .filter(Project.id == project_id)
        .first()
    )

def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    return (
        session.query(Project)
        .options(
            joinedload(Project.department),
            joinedload(Project.owner),
            joinedload(Project.assignments),
            joinedload(Project.costs),
            joinedload(Project.revenues),
            joinedload(Project.client),
            joinedload(Project.invoices),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

def update(session: Session, project_id: UUID, data: dict) -> Optional[Project]:
    prj = get_by_id(session, project_id)
    if not prj:
        return None
    for key, value in data.items():
        setattr(prj, key, value)
    session.commit()
    session.refresh(prj)
    return prj

def delete(session: Session, project_id: UUID) -> bool:
    prj = get_by_id(session, project_id)
    if prj:
        session.delete(prj)
        session.commit()
        return True
    return False
