from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import date
from typing import Optional
from decimal import Decimal


class ProjectBase(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    project_type: Optional[str] = Field(None, max_length=50)
    department_id: Optional[UUID] = None
    owner_employee_id: Optional[UUID] = None
    budget_allocated: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = Field("active", max_length=20)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    end_date: Optional[date] = None
