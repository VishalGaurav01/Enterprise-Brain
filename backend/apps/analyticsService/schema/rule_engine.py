from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from uuid import UUID

class BusinessRuleBase(BaseModel):
    rule_name: str = Field(..., max_length=255)
    entity_type: str = Field(..., max_length=50)
    condition: Dict[str, Any]
    action: Dict[str, Any]
    priority: int = 1
    enabled: bool = True

    model_config = ConfigDict(from_attributes=True)

class BusinessRuleCreate(BusinessRuleBase):
    pass

class BusinessRuleGet(BusinessRuleBase):
    rule_id: UUID

class EvaluationRequest(BaseModel):
    # This is optional depending on entity_type
    entity_type: str
    employee_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    is_organization: Optional[bool] = False

class EvaluationResponse(BaseModel):
    result: Any
    details: Dict[str, Any] = {}
    triggered_rules: list[str] = []
