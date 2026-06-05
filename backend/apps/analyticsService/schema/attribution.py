from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class AttributionBase(BaseModel):
    employee_id: UUID
    project_id: UUID
    attributed_revenue: float = 0.0
    roi_percentage: float = 0.0
    utilization_percentage: float = 0.0

class AttributionGet(AttributionBase):
    id: UUID
    calculated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
