from sqlalchemy.orm import Session
from uuid import UUID
from apps.analyticsService.model.rule_engine import RuleEngineConfig
from apps.analyticsService.schema.rule_engine import RuleEngineConfigCreate
from typing import List, Optional

def get_rule(db: Session, rule_id: UUID) -> Optional[RuleEngineConfig]:
    return db.query(RuleEngineConfig).filter(RuleEngineConfig.id == rule_id).first()

def get_rule_by_name(db: Session, rule_name: str) -> Optional[RuleEngineConfig]:
    return db.query(RuleEngineConfig).filter(RuleEngineConfig.rule_name == rule_name, RuleEngineConfig.is_active == True).first()

def get_all_rules(db: Session) -> List[RuleEngineConfig]:
    return db.query(RuleEngineConfig).all()

def create_rule(db: Session, rule: RuleEngineConfigCreate) -> RuleEngineConfig:
    db_rule = RuleEngineConfig(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def update_rule_activity(db: Session, rule_id: UUID, is_active: bool) -> Optional[RuleEngineConfig]:
    rule = get_rule(db, rule_id)
    if rule:
        rule.is_active = is_active
        db.commit()
        db.refresh(rule)
    return rule
