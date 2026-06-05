import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from core.config import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True) # ID of user who performed action
    action = Column(String(50), nullable=False) # e.g. 'CREATE', 'UPDATE', 'EVALUATE_RULE'
    entity = Column(String(100), nullable=False) # e.g. 'RuleEngineConfig', 'Employee'
    entity_id = Column(UUID(as_uuid=True)) # ID of the affected record
    changes = Column(JSONB) # Store before/after or payload
    created_at = Column(DateTime, default=datetime.utcnow)

class UserAccess(Base):
    __tablename__ = "user_access"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    login_time = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50))
    user_agent = Column(String(255))
