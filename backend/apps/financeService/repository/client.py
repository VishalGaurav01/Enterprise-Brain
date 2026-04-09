from sqlalchemy.orm import Session, joinedload
from apps.financeService.model.client import Client
from uuid import UUID
from typing import List, Optional

def create(session: Session, client: Client) -> Client:
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

def get_by_id(session: Session, client_id: UUID) -> Optional[Client]:
    return session.query(Client).options(
        joinedload(Client.invoices),
        joinedload(Client.revenues),
        joinedload(Client.projects)
    ).filter(Client.id == client_id).first()

def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[Client]:
    return session.query(Client).options(
        joinedload(Client.invoices),
        joinedload(Client.revenues),
        joinedload(Client.projects)
    ).offset(skip).limit(limit).all()

def update(session: Session, client_id: UUID, data: dict) -> Optional[Client]:
    client = get_by_id(session, client_id)
    if not client:
        return None
    for key, value in data.items():
        if hasattr(client, key):
            setattr(client, key, value)
    session.commit()
    session.refresh(client)
    return client

def delete(session: Session, client_id: UUID) -> bool:
    client = get_by_id(session, client_id)
    if client:
        session.delete(client)
        session.commit()
        return True
    return False
