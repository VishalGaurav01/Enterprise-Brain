from sqlalchemy.orm import Session
from typing import Dict, Any, Tuple, List
from uuid import UUID
import operator

from apps.analyticsService.repository.rule_engine import get_rules_by_entity_type
from apps.analyticsService.service.rule_evaluator import get_entity_metrics
from apps.shared.kafka_producer import event_bus

OPERATORS = {
    "<": operator.lt,
    ">": operator.gt,
    "==": operator.eq,
    "<=": operator.le,
    ">=": operator.ge,
    "!=": operator.ne
}

def evaluate_entity_rules(
    db: Session, 
    entity_type: str,
    employee_id: UUID = None,
    project_id: UUID = None,
    department_id: UUID = None,
    is_organization: bool = False
) -> Tuple[Dict[str, float], Dict[str, Any], List[str]]:
    
    # 1. Resolve entity ID
    entity_id = employee_id or project_id or department_id

    # 2. Fetch facts / metrics
    metrics = get_entity_metrics(db, entity_type, entity_id, is_organization)

    # 3. Fetch rules
    rules = get_rules_by_entity_type(db, entity_type)

    triggered_rules = []
    
    context = {
        "entity_type": entity_type,
        "entity_id": str(entity_id) if entity_id else None,
        "is_organization": is_organization,
        "metrics": metrics
    }

    # 4. Evaluate rules
    for rule in rules:
        cond = rule.condition
        metric_name = cond.get("metric")
        op_str = cond.get("operator")
        threshold = cond.get("value")

        if metric_name in metrics:
            val = metrics[metric_name]
            op_func = OPERATORS.get(op_str)
            if op_func and op_func(val, threshold):
                triggered_rules.append(rule.rule_name)
                # 5. Broadcast to Event Bus
                event_bus.publish_action(rule.action, context)

    # Return primary result (for backward compatibility or dashboard display)
    # We just return the first available metric as 'result' for simplicity, and full metrics in details
    primary_result = list(metrics.values())[0] if metrics else 0.0

    return primary_result, metrics, triggered_rules
