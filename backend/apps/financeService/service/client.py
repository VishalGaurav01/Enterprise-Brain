from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from apps.financeService.model.client import Client
from apps.financeService.schema.client import ClientCreate, ClientUpdate
from apps.shared.responses import ClientGet
from apps.financeService.repository import client as repo
from apps.authService.schema.auth import UserGet

def create_client(session: Session, data: ClientCreate, current_user: UserGet) -> ClientGet:
    client = Client(**data.model_dump())
    client.created_by = current_user.id
    created = repo.create(session, client)
    return ClientGet.model_validate(created)

def get_all_clients(session: Session, skip: int = 0, limit: int = 100) -> List[ClientGet]:
    clients = repo.get_all(session, skip, limit)
    return [ClientGet.model_validate(c) for c in clients]

def get_client_by_id(session: Session, client_id: UUID) -> Optional[ClientGet]:
    client = repo.get_by_id(session, client_id)
    return ClientGet.model_validate(client) if client else None

def update_client_details(session: Session, client_id: UUID, data: ClientUpdate) -> Optional[ClientGet]:
    updated_data = data.model_dump(exclude_unset=True)
    updated = repo.update(session, client_id, updated_data)
    return ClientGet.model_validate(updated) if updated else None

def delete_client_record(session: Session, client_id: UUID) -> bool:
    return repo.delete(session, client_id)
