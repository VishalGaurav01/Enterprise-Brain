from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from apps.analyticsService.model.business_rule import BusinessRule
from apps.analyticsService.schema.rule_engine import BusinessRuleCreate

def get_rule(db: Session, rule_id: UUID) -> Optional[BusinessRule]:
    return db.query(BusinessRule).filter(BusinessRule.rule_id == rule_id).first()

def get_rules_by_entity_type(db: Session, entity_type: str) -> List[BusinessRule]:
    return db.query(BusinessRule).filter(BusinessRule.entity_type == entity_type, BusinessRule.enabled == True).order_by(BusinessRule.priority.desc()).all()

def get_all_rules(db: Session) -> List[BusinessRule]:
    return db.query(BusinessRule).all()

def create_rule(db: Session, rule: BusinessRuleCreate) -> BusinessRule:
    db_rule = BusinessRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def update_rule_activity(db: Session, rule_id: UUID, enabled: bool) -> Optional[BusinessRule]:
    rule = get_rule(db, rule_id)
    if rule:
        rule.enabled = enabled
        db.commit()
        db.refresh(rule)
    return rule
