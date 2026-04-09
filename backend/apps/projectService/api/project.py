from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from core.database import get_db
from apps.shared.customResponse import custom_response
from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet
from apps.projectService.schema.project import ProjectCreate, ProjectUpdate
from apps.shared.responses import ProjectGet
from apps.projectService.service import project as service

router = APIRouter(prefix="/projects", tags=["Project Management"])

@router.post("/")
def create_endpoint(
    data: ProjectCreate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_project(session, data, current_user)
        return custom_response(result, "Project created successfully", 200)
    except Exception as e:
        return custom_response(None, "Project creation failed", 500, str(e))

@router.get("/")
def list_endpoint(
    skip: int = 0, limit: int = 100, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_all_projects(session, skip, limit)
        return custom_response(results, "Projects retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to retrieve projects", 500, str(e))

@router.get("/{id}")
def get_endpoint(
    id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.get_project_by_id(session, id)
        if not result:
            return custom_response(None, "Project not found", 404)
        return custom_response(result, "Project retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Project retrieval failed", 500, str(e))

@router.patch("/{id}")
def update_endpoint(
    id: UUID, 
    data: ProjectUpdate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.update_project_details(session, id, data)
        if not result:
            return custom_response(None, "Project not found", 404)
        return custom_response(result, "Project updated successfully", 200)
    except Exception as e:
        return custom_response(None, "Update failed", 500, str(e))

@router.delete("/{id}")
def delete_endpoint(
    id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        success = service.delete_project_record(session, id)
        if not success:
            return custom_response(None, "Project not found", 404)
        return custom_response(None, "Project deleted successfully", 200)
    except Exception as e:
        return custom_response(None, "Deletion failed", 500, str(e))
