from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from decimal import Decimal
from typing import Optional


class ReimbursementBase(BaseModel):
    employee_id: UUID
    expense_id: UUID
    claim_amount: Decimal = Field(..., gt=0)
    status: Optional[str] = Field("pending", max_length=50)
    description: Optional[str] = Field(None, max_length=255)

    model_config = ConfigDict(from_attributes=True)


class ReimbursementCreate(ReimbursementBase):
    pass


class ReimbursementUpdate(BaseModel):
    claim_amount: Optional[Decimal] = Field(None, gt=0)
    status: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)

    model_config = ConfigDict(from_attributes=True)
