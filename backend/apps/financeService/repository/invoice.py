from sqlalchemy.orm import Session, joinedload
from apps.financeService.model.invoice import Invoice
from uuid import UUID
from typing import List, Optional

def create(session: Session, invoice: Invoice) -> Invoice:
    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    return invoice

def get_by_id(session: Session, inv_id: UUID) -> Optional[Invoice]:
    return session.query(Invoice).options(
        joinedload(Invoice.client),
        joinedload(Invoice.revenues)
    ).filter(Invoice.id == inv_id).first()

def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Invoice]:
    return session.query(Invoice).options(
        joinedload(Invoice.client),
        joinedload(Invoice.revenues)
    ).offset(skip).limit(limit).all()

def delete(session: Session, inv_id: UUID) -> bool:
    inv = get_by_id(session, inv_id)
    if inv:
        session.delete(inv)
        session.commit()
        return True
    return False
