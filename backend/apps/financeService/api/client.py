from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from core.database import get_db
from apps.shared.customResponse import custom_response
from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet
from apps.financeService.schema.client import ClientCreate, ClientUpdate
from apps.shared.responses import ClientGet
from apps.financeService.service import client as service

router = APIRouter(prefix="/clients", tags=["Client Management"])

@router.post("/")
def create_endpoint(
    data: ClientCreate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_client(session, data, current_user)
        return custom_response(result, "Client created successfully", 200)
    except Exception as e:
        return custom_response(None, "Client creation failed", 500, str(e))

@router.get("/")
def list_endpoint(
    skip: int = 0, limit: int = 100, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_all_clients(session, skip, limit)
        return custom_response(results, "Clients retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to fetch clients", 500, str(e))

@router.get("/{id}")
def get_endpoint(
    id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.get_client_by_id(session, id)
        if not result:
            return custom_response(None, "Client not found", 404)
        return custom_response(result, "Client retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to fetch client", 500, str(e))

@router.patch("/{id}")
def update_endpoint(
    id: UUID, 
    data: ClientUpdate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.update_client_details(session, id, data)
        if not result:
            return custom_response(None, "Client not found", 404)
        return custom_response(result, "Client updated successfully", 200)
    except Exception as e:
        return custom_response(None, "Update failed", 500, str(e))

@router.delete("/{id}")
def delete_endpoint(
    id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        service.delete_client_record(session, id)
        return custom_response(None, "Client deleted successfully", 200)
    except Exception as e:
        return custom_response(None, "Deletion failed", 500, str(e))
