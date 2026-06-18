from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import date
from typing import Optional
from decimal import Decimal


class AssignmentBase(BaseModel):
    employee_id: UUID
    project_id: UUID
    role: Optional[str] = Field(None, max_length=100)
    allocation_percent: Optional[Decimal] = Field(None, ge=0)
    billing_rate: Optional[Decimal] = Field(None, ge=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    contribution_type: Optional[str] = Field(None, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(BaseModel):
    role: Optional[str] = None
    allocation_percent: Optional[Decimal] = None
    billing_rate: Optional[Decimal] = None
