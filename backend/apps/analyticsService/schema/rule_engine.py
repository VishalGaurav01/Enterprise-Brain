from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class RuleEngineConfigBase(BaseModel):
    rule_name: str
    expression: str
    description: Optional[str] = None
    version: int = 1
    is_active: bool = True

class RuleEngineConfigCreate(RuleEngineConfigBase):
    pass

class RuleEngineConfigGet(RuleEngineConfigBase):
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)

class EvaluationRequest(BaseModel):
    employee_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    is_organization: bool = False
    rule_name: str

class EvaluationResponse(BaseModel):
    result: float
    details: dict
