import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, String, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from core.config import Base

class EmployeeProjectAssignment(Base):
    __tablename__ = "employee_project_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"), index=True)
    # Changed from "projects.id" to "project.id" to match the actual tablename
    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id"), index=True)
    role = Column(String(100))
    allocation_percent = Column(Numeric(5, 2))
    billing_rate = Column(Numeric(15, 2))
    start_date = Column(Date)
    end_date = Column(Date)
    contribution_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))

    # Relationships
    employee = relationship("Employee", back_populates="assignments")
    project = relationship("Project", back_populates="assignments")
