from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from core.database import get_db
from apps.shared.customResponse import custom_response
from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet
from apps.projectService.schema.vendor import VendorCreate, VendorUpdate
from apps.shared.responses import VendorGet
from apps.projectService.service import vendor as service

router = APIRouter(prefix="/vendors", tags=["Vendor Management"])

@router.post("/")
def create_endpoint(
    data: VendorCreate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_vendor(session, data, current_user)
        return custom_response(result, "Vendor created successfully", 200)
    except Exception as e:
        return custom_response(None, "Vendor creation failed", 500, str(e))

@router.get("/")
def list_endpoint(
    skip: int = 0, limit: int = 100, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_all_vendors(session, skip, limit)
        return custom_response(results, "Vendors retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to retrieve vendors", 500, str(e))

@router.get("/{id}")
def get_endpoint(
    id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.get_vendor_by_id(session, id)
        if not result:
            return custom_response(None, "Vendor not found", 404)
        return custom_response(result, "Vendor retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Vendor retrieval failed", 500, str(e))

@router.patch("/{id}")
def update_endpoint(
    id: UUID, 
    data: VendorUpdate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.update_vendor_details(session, id, data)
        if not result:
            return custom_response(None, "Vendor not found", 404)
        return custom_response(result, "Vendor updated successfully", 200)
    except Exception as e:
        return custom_response(None, "Update failed", 500, str(e))

@router.delete("/{id}")
def delete_endpoint(
    id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        service.delete_vendor_record(session, id)
        return custom_response(None, "Vendor deleted successfully", 200)
    except Exception as e:
        return custom_response(None, "Deletion failed", 500, str(e))
