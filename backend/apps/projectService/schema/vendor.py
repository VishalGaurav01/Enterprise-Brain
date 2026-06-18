from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional

class VendorBase(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    service_type: Optional[str] = Field(None, max_length=50)

    model_config = ConfigDict(from_attributes=True)

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    service_type: Optional[str] = None
