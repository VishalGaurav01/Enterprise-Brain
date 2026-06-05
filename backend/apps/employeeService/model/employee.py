import uuid
from datetime import datetime
from sqlalchemy import String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from core.config import Base
from apps.projectService.model.project import Project

class Employee(Base):
    __tablename__ = "employee"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_code = Column(String(50), unique=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True, index=True)
    contact_number = Column(String(20), unique=True, index=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("department.id"), index=True)
    designation_id = Column(UUID(as_uuid=True), ForeignKey("designation.id"), index=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"), index=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))

    department = relationship(
        "Department", back_populates="employees", foreign_keys=[department_id]
    )
    designation = relationship(
        "Designation", back_populates="employees", foreign_keys=[designation_id]
    )
    manager = relationship(
        "Employee",
        remote_side=[id],
        back_populates="subordinates",
    )
    subordinates = relationship("Employee", back_populates="manager")
    
    projects = relationship(
        "Project", back_populates="owner", foreign_keys=[Project.owner_employee_id]
    )
    
    assignments = relationship("EmployeeProjectAssignment", back_populates="employee")
    reimbursements = relationship("Reimbursement", back_populates="employee")
