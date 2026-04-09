from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import date
from decimal import Decimal
from typing import Optional

class ProjectRevenueBase(BaseModel):
    project_id: UUID
    client_id: UUID
    invoice_id: UUID
    revenue_amount: Decimal = Field(..., gt=0)
    recognized_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectRevenueCreate(ProjectRevenueBase):
    pass
