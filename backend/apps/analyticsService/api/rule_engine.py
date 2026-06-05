from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from apps.shared.security import verify_token
from apps.authService.schema.auth import UserGet
from apps.analyticsService.schema.rule_engine import RuleEngineConfigCreate, RuleEngineConfigGet, EvaluationRequest, EvaluationResponse
from apps.analyticsService.repository.rule_engine import create_rule, get_all_rules, get_rule_by_name
from apps.analyticsService.service.rule_evaluator import evaluate_rule, get_employee_context

router = APIRouter()

@router.post("/rules", response_model=RuleEngineConfigGet)
def add_rule(
    rule: RuleEngineConfigCreate,
    db: Session = Depends(get_db),
    current_user: UserGet = Depends(verify_token)
):
    return create_rule(db, rule)

@router.get("/rules", response_model=List[RuleEngineConfigGet])
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
    rule = get_rule_by_name(db, request.rule_name)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found or inactive")
        
    try:
        result = evaluate_rule(
            db=db, 
            rule_expression=rule.expression, 
            employee_id=request.employee_id, 
            project_id=request.project_id,
            department_id=request.department_id,
            is_organization=request.is_organization
        )
        
        details = {}
        if request.employee_id:
            from apps.analyticsService.service.rule_evaluator import get_employee_context
            details = get_employee_context(db, request.employee_id)
        elif request.project_id:
            from apps.analyticsService.service.rule_evaluator import get_project_context
            details = get_project_context(db, request.project_id)
        elif request.department_id:
            from apps.analyticsService.service.rule_evaluator import get_department_context
            details = get_department_context(db, request.department_id)
        elif request.is_organization:
            from apps.analyticsService.service.rule_evaluator import get_organization_context
            details = get_organization_context(db)
            
        return EvaluationResponse(result=result, details=details)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
