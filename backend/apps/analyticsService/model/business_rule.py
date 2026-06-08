import uuid
from sqlalchemy import Column, String, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from core.config import Base

class BusinessRule(Base):
    __tablename__ = "business_rule"

    rule_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    rule_name = Column(String(255), unique=True, index=True, nullable=False)
    entity_type = Column(String(50), nullable=False) # e.g., 'department', 'employee', 'project', 'organization'
    condition = Column(JSONB, nullable=False)        # e.g., {"metric": "department_roi", "operator": "<", "value": 40}
    action = Column(JSONB, nullable=False)           # e.g., {"recommendation": "budget_review"}
    priority = Column(Integer, default=1)
    enabled = Column(Boolean, default=True)
