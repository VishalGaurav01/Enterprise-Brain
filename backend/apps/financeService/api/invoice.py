from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from core.database import get_db
from apps.shared.customResponse import custom_response
from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet
from apps.financeService.schema.invoice import InvoiceCreate
from apps.shared.responses import InvoiceGet
from apps.financeService.service import invoice as service

router = APIRouter(prefix="/invoices", tags=["Invoice Management"])

@router.post("/")
def create_endpoint(
    data: InvoiceCreate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_invoice(session, data, current_user)
        return custom_response(result, "Invoice created successfully", 200)
    except Exception as e:
        return custom_response(None, "Invoice creation failed", 500, str(e))

@router.get("/")
def list_endpoint(
    skip: int = 0, limit: int = 100, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        results = service.get_all_invoices(session, skip, limit)
        return custom_response(results, "Invoices retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to fetch invoices", 500, str(e))

@router.delete("/{id}")
def delete_endpoint(
    id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        service.delete_invoice_record(session, id)
        return custom_response(None, "Invoice record deleted", 200)
    except Exception as e:
        return custom_response(None, "Deletion failed", 500, str(e))
