from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any

class AuditLogGet(BaseModel):
    id: UUID
    user_id: UUID
    action: str
    entity: str
    entity_id: Optional[UUID] = None
    changes: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserAccessGet(BaseModel):
    id: UUID
    user_id: UUID
    login_time: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
