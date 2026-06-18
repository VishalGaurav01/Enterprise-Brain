from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from decimal import Decimal
from typing import Optional


class SoftwareToolBase(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    department_id: UUID
    annual_cost: Decimal = Field(..., gt=0)

    model_config = ConfigDict(from_attributes=True)


class SoftwareToolCreate(SoftwareToolBase):
    pass


class SoftwareToolUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    department_id: Optional[UUID] = None
    annual_cost: Optional[Decimal] = Field(None, gt=0)

    model_config = ConfigDict(from_attributes=True)
