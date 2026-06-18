from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional

class DepartmentBase(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status: Optional[str] = Field("active", max_length=20)

    model_config = ConfigDict(from_attributes=True)

class DepartmentCreate(DepartmentBase):
    pass
