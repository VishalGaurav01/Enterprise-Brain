import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from core.config import Base

class ProjectRevenue(Base):
    __tablename__ = "project_revenue"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id"), index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("client.id"), index=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoice.id"), index=True)
    revenue_amount = Column(Numeric(15, 2), nullable=False)
    recognized_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))

    # Relationships
    project = relationship("Project", back_populates="revenues")
    client = relationship("Client", back_populates="revenues")
    invoice = relationship("Invoice", back_populates="revenues")
