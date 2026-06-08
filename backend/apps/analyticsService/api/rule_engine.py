from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet
from apps.analyticsService.schema.rule_engine import BusinessRuleCreate, BusinessRuleGet, EvaluationRequest, EvaluationResponse
from apps.analyticsService.repository.rule_engine import create_rule, get_all_rules
from apps.analyticsService.service.decision_engine import evaluate_entity_rules

router = APIRouter()

@router.post("/rules", response_model=BusinessRuleGet)
def add_rule(
    rule: BusinessRuleCreate,
    db: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    return create_rule(db, rule)

@router.get("/rules", response_model=List[BusinessRuleGet])
def list_rules(
    db: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    return get_all_rules(db)

@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate(
    request: EvaluationRequest,
    db: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    try:
        result, details, triggered = evaluate_entity_rules(
            db=db,
            entity_type=request.entity_type,
            employee_id=request.employee_id,
            project_id=request.project_id,
            department_id=request.department_id,
            is_organization=request.is_organization
        )
        return EvaluationResponse(result=result, details=details, triggered_rules=triggered)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
