import uuid
from datetime import datetime
from sqlalchemy import String, Column, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from core.config import Base

class Vendor(Base):
    __tablename__ = "vendor"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    service_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))

    # Relationships
    costs = relationship("ProjectCost", back_populates="vendor")
