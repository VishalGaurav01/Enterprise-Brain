from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from apps.financeService.model.invoice import Invoice
from apps.financeService.schema.invoice import InvoiceCreate
from apps.shared.responses import InvoiceGet
from apps.financeService.repository import invoice as repo
from apps.authService.schema.auth import UserGet

def create_invoice(session: Session, data: InvoiceCreate, current_user: UserGet) -> InvoiceGet:
    inv = Invoice(**data.model_dump())
    inv.created_by = current_user.id
    created = repo.create(session, inv)
    return InvoiceGet.model_validate(created)

def get_all_invoices(session: Session, skip: int = 0, limit: int = 100) -> List[InvoiceGet]:
    invs = repo.get_all(session, skip, limit)
    return [InvoiceGet.model_validate(i) for i in invs]

def get_invoice_by_id(session: Session, inv_id: UUID) -> Optional[InvoiceGet]:
    inv = repo.get_by_id(session, inv_id)
    return InvoiceGet.model_validate(inv) if inv else None

def delete_invoice_record(session: Session, inv_id: UUID) -> bool:
    return repo.delete(session, inv_id)
