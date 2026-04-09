import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Column, DateTime
from sqlalchemy.orm import relationship
from core.config import Base
from datetime import datetime
from apps.employeeService.model.employee import Employee


class Designation(Base):
    __tablename__ = "designation"

    id = Column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    name = Column(String(100), unique=True, index=True)
    description = Column(String(255))
    grade = Column(String(50))
    pay_band = Column(String(50))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    employees = relationship(
        "Employee", back_populates="designation", foreign_keys=[Employee.designation_id]
    )
