import uuid
from sqlalchemy import String, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from core.config import Base


class Client(Base):
    __tablename__ = "client"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    company_name = Column(String(150), nullable=False, index=True)
    industry = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))

    # Relationships
    invoices = relationship("Invoice", back_populates="client")
    revenues = relationship("ProjectRevenue", back_populates="client")
    projects = relationship("Project", back_populates="client")
