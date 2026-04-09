from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import date
from decimal import Decimal
from typing import Optional

class InvoiceBase(BaseModel):
    client_id: UUID
    amount: Decimal = Field(..., gt=0)
    due_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

class InvoiceCreate(InvoiceBase):
    pass
