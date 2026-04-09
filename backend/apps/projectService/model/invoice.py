import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from core.config import Base

class Invoice(Base):
    __tablename__ = "invoice"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("client.id"), index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id"), index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    due_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))

    # Relationships
    client = relationship("Client", back_populates="invoices")
    project = relationship("Project", back_populates="invoices")
    revenues = relationship("ProjectRevenue", back_populates="invoice")
