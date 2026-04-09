import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, Numeric, String, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from core.config import Base

class ProjectCost(Base):
    __tablename__ = "project_cost"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id"), index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor.id"), index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    cost_type = Column(String(50))
    expense_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))

    # Relationships
    project = relationship("Project", back_populates="costs")
    vendor = relationship("Vendor", back_populates="costs")
