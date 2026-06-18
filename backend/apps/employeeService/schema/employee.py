from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID

class EmployeeBase(BaseModel):
    user_code: Optional[str] = Field(None, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    contact_number: Optional[str] = Field(None, max_length=20)
    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    status: Optional[str] = Field("active", max_length=20)

    model_config = ConfigDict(from_attributes=True)

class EmployeeCreate(EmployeeBase):
    created_by: Optional[UUID] = None

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    contact_number: Optional[str] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class EmployeeDelete(EmployeeBase):
    id: UUID