from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from apps.projectService.model.project import Project
from apps.projectService.schema.project import ProjectCreate, ProjectUpdate
from apps.shared.responses import ProjectGet
from apps.projectService.repository import project as repo
from apps.authService.schema.auth import UserGet

def create_project(session: Session, data: ProjectCreate, current_user: UserGet) -> ProjectGet:
    prj = Project(**data.model_dump())
    prj.created_by = current_user.id
    created = repo.create(session, prj)
    return ProjectGet.model_validate(created)

def get_all_projects(session: Session, skip: int = 0, limit: int = 100) -> List[ProjectGet]:
    projects = repo.get_all(session, skip, limit)
    return [ProjectGet.model_validate(p) for p in projects]

def get_project_by_id(session: Session, project_id: UUID) -> Optional[ProjectGet]:
    prj = repo.get_by_id(session, project_id)
    return ProjectGet.model_validate(prj) if prj else None

def update_project_details(session: Session, project_id: UUID, data: ProjectUpdate) -> Optional[ProjectGet]:
    updated_data = data.model_dump(exclude_unset=True)
    updated = repo.update(session, project_id, updated_data)
    return ProjectGet.model_validate(updated) if updated else None

def delete_project_record(session: Session, project_id: UUID) -> bool:
    return repo.delete(session, project_id)
