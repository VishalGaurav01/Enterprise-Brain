from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional

class DesignationBase(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    grade: Optional[str] = Field(None, max_length=50)
    pay_band: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field("active", max_length=20)

    model_config = ConfigDict(from_attributes=True)

class DesignationCreate(DesignationBase):
    pass
