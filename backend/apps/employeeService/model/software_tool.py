import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from core.config import Base


class SoftwareTool(Base):
    __tablename__ = "software_tool"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False, index=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("department.id"), nullable=False, index=True)
    annual_cost = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))

    # Relationships
    department = relationship("Department", back_populates="software_tools")
