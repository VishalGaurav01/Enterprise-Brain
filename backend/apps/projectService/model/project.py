import uuid
from datetime import datetime
from sqlalchemy import String, Column, ForeignKey, DateTime, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from core.config import Base

class Project(Base):
    __tablename__ = "project"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(100), index=True)
    project_type = Column(String(50))
    department_id = Column(UUID(as_uuid=True), ForeignKey("department.id"), index=True)
    owner_employee_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"), index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("client.id"), index=True)
    budget_allocated = Column(Numeric(15, 2))
    status = Column(String(20), default="active")
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))

    # Relationships
    department = relationship("Department", back_populates="projects")
    owner = relationship("Employee", back_populates="projects")
    client = relationship("Client", back_populates="projects")
    assignments = relationship("EmployeeProjectAssignment", back_populates="project")
    costs = relationship("ProjectCost", back_populates="project")
    revenues = relationship("ProjectRevenue", back_populates="project")
    invoices = relationship("Invoice", back_populates="project")
