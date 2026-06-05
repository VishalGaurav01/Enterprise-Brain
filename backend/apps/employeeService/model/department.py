import uuid
from core.config import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from apps.employeeService.model.employee import Employee
from apps.projectService.model.project import Project


class Department(Base):
    __tablename__ = "department"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, index=True)
    description = Column(String(255))
    status = Column(String(20), default="active")
    cost_center_code = Column(String(50), unique=True, index=True)
    head_employee_id = Column(
        UUID(as_uuid=True), ForeignKey("employee.id"), index=True, nullable=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    employees = relationship(
        "Employee", back_populates="department", foreign_keys=[Employee.department_id]
    )
    projects = relationship(
        "Project", back_populates="department", foreign_keys=[Project.department_id]
    )
    software_tools = relationship("SoftwareTool", back_populates="department")
