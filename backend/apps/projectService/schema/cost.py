from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import date
from typing import Optional
from decimal import Decimal

class ProjectCostBase(BaseModel):
    project_id: UUID
    vendor_id: UUID
    amount: Decimal = Field(..., gt=0)
    cost_type: Optional[str] = Field(None, max_length=50)
    expense_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectCostCreate(ProjectCostBase):
    pass

class ProjectCostUpdate(BaseModel):
    amount: Optional[Decimal] = None
    cost_type: Optional[str] = None
    expense_date: Optional[date] = None
