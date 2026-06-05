import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from core.config import Base


class Reimbursement(Base):
    __tablename__ = "reimbursement"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False, index=True)
    expense_id = Column(UUID(as_uuid=True), nullable=False, index=True)          # References external expense record
    claim_amount = Column(Numeric(15, 2), nullable=False)
    status = Column(String(30), nullable=False, default="pending")               # pending | approved | rejected
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))

    # Relationships
    employee = relationship("Employee", back_populates="reimbursements")
