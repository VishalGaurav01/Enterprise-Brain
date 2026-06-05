import uuid
from sqlalchemy import Column, String, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from core.config import Base

class RuleEngineConfig(Base):
    __tablename__ = "rule_engine_config"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    rule_name = Column(String(255), unique=True, index=True, nullable=False)
    expression = Column(Text, nullable=False)
    description = Column(String(500))
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
