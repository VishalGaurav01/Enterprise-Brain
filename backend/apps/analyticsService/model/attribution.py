import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from core.config import Base

class EmployeeRevenueAttribution(Base):
    __tablename__ = "employee_revenue_attribution"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"), index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id"), index=True)
    
    attributed_revenue = Column(Numeric(15, 2), default=0.0)
    roi_percentage = Column(Numeric(10, 2), default=0.0)
    utilization_percentage = Column(Numeric(5, 2), default=0.0)
    
    calculated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    employee = relationship("Employee")
    project = relationship("Project")
