import uuid
import secrets
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from apps.authService.model.auth import User, Role, Permission, Session as AuthSession
from apps.authService.schema.auth import (
    UserCreate, UserGet, UserUpdate, UserLogin, TokenResponse,
    RoleCreate, RoleGet, RoleUpdate,
    PermissionCreate, PermissionGet
)
from apps.authService.repository import auth as repo

import bcrypt

# Password hashing configuration
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== AUTH Logic ====================
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

# ==================== USER Service ====================
def register_user(session: Session, data: UserCreate) -> UserGet:
    if repo.get_user_by_username(session, data.username):
        raise ValueError(f"Username {data.username} already taken")
    if repo.get_user_by_email(session, data.email):
        raise ValueError(f"Email {data.email} already registered")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    created = repo.create_user(session, user)
    return UserGet.model_validate(created)

def authenticate_user(session: Session, data: UserLogin) -> TokenResponse:
    user = repo.get_user_by_username(session, data.username)
    if not user:
        # Fallback: try finding user by email instead
        user = repo.get_user_by_email(session, data.username)
        
    if not user or not verify_password(data.password, user.hashed_password):
        raise ValueError("Invalid username or password")

    expires_at = datetime.utcnow() + timedelta(hours=24)
    auth_session = AuthSession(
        user_id=user.id,
        session_token=generate_session_token(),
        expires_at=expires_at
    )
    repo.create_session(session, auth_session)

    return TokenResponse(
        session_token=auth_session.session_token,
        user=UserGet.model_validate(user),
        expires_at=expires_at
    )

def get_all_users(session: Session, skip: int = 0, limit: int = 100) -> List[UserGet]:
    users = repo.get_all_users(session, skip, limit)
    return [UserGet.model_validate(u) for u in users]

def get_user_profile(session: Session, user_id: uuid.UUID) -> Optional[UserGet]:
    user = repo.get_user_complete_info(session, user_id)
    return UserGet.model_validate(user) if user else None

def update_user_details(session: Session, user_id: uuid.UUID, data: UserUpdate) -> Optional[UserGet]:
    updated = repo.update_user(session, user_id, data.model_dump(exclude_unset=True))
    return UserGet.model_validate(updated) if updated else None

def delete_user_account(session: Session, user_id: uuid.UUID) -> bool:
    return repo.delete_user(session, user_id)

def assign_role_to_user(session: Session, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
    return repo.add_role_to_user(session, user_id, role_id)

def remove_user_role(session: Session, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
    return repo.remove_role_to_user(session, user_id, role_id)

def remove_user_roles_bulk(session: Session, user_id: uuid.UUID, role_ids: List[uuid.UUID]) -> bool:
    return repo.remove_bulk_role_to_user(session, user_id, role_ids)

# ==================== ROLE Service ====================
def create_role(session: Session, data: RoleCreate) -> RoleGet:
    role = Role(**data.model_dump())
    created = repo.create_role(session, role)
    return RoleGet.model_validate(created)

def get_all_roles(session: Session) -> List[RoleGet]:
    roles = repo.get_all_roles(session)
    return [RoleGet.model_validate(r) for r in roles]

def get_role_details(session: Session, role_id: uuid.UUID) -> Optional[RoleGet]:
    role = repo.get_role_complete_info(session, role_id)
    return RoleGet.model_validate(role) if role else None

def assign_permission_to_role(session: Session, role_id: uuid.UUID, perm_id: uuid.UUID) -> bool:
    return repo.add_permission_to_role(session, role_id, perm_id)

def remove_role_permission(session: Session, role_id: uuid.UUID, perm_id: uuid.UUID) -> bool:
    return repo.remove_permission_to_role(session, role_id, perm_id)

def remove_role_permissions_bulk(session: Session, role_id: uuid.UUID, perm_ids: List[uuid.UUID]) -> bool:
    return repo.remove_bulk_permission_to_role(session, role_id, perm_ids)

def delete_role(session: Session, role_id: uuid.UUID) -> bool:
    return repo.delete_role(session, role_id)

# ==================== PERMISSION Service ====================
def create_permission(session: Session, data: PermissionCreate) -> PermissionGet:
    perm = Permission(**data.model_dump())
    created = repo.create_permission(session, perm)
    return PermissionGet.model_validate(created)

def get_all_permissions(session: Session) -> List[PermissionGet]:
    perms = repo.get_all_permissions(session)
    return [PermissionGet.model_validate(p) for p in perms]

def delete_permission(session: Session, perm_id: uuid.UUID) -> bool:
    return repo.delete_permission(session, perm_id)
