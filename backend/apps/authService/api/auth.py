from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from core.database import get_db
from apps.shared.customResponse import custom_response
from apps.shared.security import verify_token
from apps.authService.schema.auth import (
    UserCreate, UserLogin, UserUpdate, UserGet,
    RoleCreate, RoleUpdate, 
    PermissionCreate
)
from apps.authService.service import auth as service

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

# ==================== AUTH ENTRIES ====================
@router.post("/register")
def register_endpoint(data: UserCreate, session: Session = Depends(get_db)):
    try:
        result = service.register_user(session, data)
        return custom_response(result, "User registered successfully", 200)
    except ValueError as e:
        return custom_response(None, str(e), 400)
    except Exception as e:
        return custom_response(None, "Registration failed", 500, str(e))

@router.post("/login")
def login_endpoint(data: UserLogin, session: Session = Depends(get_db)):
    try:
        result = service.authenticate_user(session, data)
        return custom_response(result, "Login successful", 200)
    except ValueError as e:
        return custom_response(None, str(e), 401)
    except Exception as e:
        return custom_response(None, "Login failed", 500, str(e))

# ==================== USER MANAGEMENT ====================
@router.get("/users")
def list_users(
    skip: int = 0, limit: int = 100, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        users = service.get_all_users(session, skip, limit)
        return custom_response(users, "Users retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to retrieve users", 500, str(e))

@router.get("/users/{id}")
def get_user_profile(
    id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        user = service.get_user_profile(session, id)
        if not user:
            return custom_response(None, "User not found", 404)
        return custom_response(user, "User profile retrieved", 200)
    except Exception as e:
        return custom_response(None, "Profile retrieval failed", 500, str(e))

@router.put("/users/{id}")
def update_user(
    id: UUID, 
    data: UserUpdate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        user = service.update_user_details(session, id, data)
        if not user:
            return custom_response(None, "User not found", 404)
        return custom_response(user, "User updated successfully", 200)
    except Exception as e:
        return custom_response(None, "Update failed", 500, str(e))

# ==================== ROLE & PERMISSION MANAGEMENT ====================
@router.post("/roles")
def create_role_endpoint(
    data: RoleCreate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_role(session, data)
        return custom_response(result, "Role created successfully", 200)
    except Exception as e:
        return custom_response(None, "Role creation failed", 500, str(e))

@router.get("/roles")
def list_roles(
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        roles = service.get_all_roles(session)
        return custom_response(roles, "Roles retrieved successfully", 200)
    except Exception as e:
        return custom_response(None, "Failed to retrieve roles", 500, str(e))

@router.post("/permissions")
def create_permission_endpoint(
    data: PermissionCreate, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        result = service.create_permission(session, data)
        return custom_response(result, "Permission created successfully", 200)
    except Exception as e:
        return custom_response(None, "Permission creation failed", 500, str(e))

# ==================== RBAC MAPPINGS & BULK OPERATIONS ====================

@router.post("/users/{id}/roles/{role_id}")
def assign_role(
    id: UUID, 
    role_id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        success = service.assign_role_to_user(session, id, role_id)
        if success:
            return custom_response(None, "Role assigned successfully", 200)
        return custom_response(None, "User or Role not found", 404)
    except Exception as e:
        return custom_response(None, "Assignment failed", 500, str(e))

@router.delete("/users/{id}/roles/{role_id}")
def remove_role(
    id: UUID, 
    role_id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        success = service.remove_user_role(session, id, role_id)
        if success:
            return custom_response(None, "Role removed successfully", 200)
        return custom_response(None, "User or Role not found", 404)
    except Exception as e:
        return custom_response(None, "Removal failed", 500, str(e))

@router.post("/roles/{id}/permissions/{perm_id}")
def assign_permission(
    id: UUID, 
    perm_id: UUID, 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        success = service.assign_permission_to_role(session, id, perm_id)
        if success:
            return custom_response(None, "Permission assigned successfully", 200)
        return custom_response(None, "Role or Permission not found", 404)
    except Exception as e:
        return custom_response(None, "Assignment failed", 500, str(e))

@router.delete("/roles/{id}/permissions/bulk")
def remove_permissions_bulk(
    id: UUID, 
    perm_ids: List[UUID] = Query(...), 
    session: Session = Depends(get_db), 
    current_user: UserGet = Depends(verify_token)
):
    try:
        success = service.remove_role_permissions_bulk(session, id, perm_ids)
        if success:
            return custom_response(None, "Permissions removed successfully", 200)
        return custom_response(None, "Role not found or error occurred", 404)
    except Exception as e:
        return custom_response(None, "Bulk removal failed", 500, str(e))
