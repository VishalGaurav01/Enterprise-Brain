from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional

class ClientBase(BaseModel):
    company_name: Optional[str] = Field(None, max_length=150)
    industry: Optional[str] = Field(None, max_length=100)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
