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

import os
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

@router.get("/graph-data")
def get_graph_data(current_user: UserGet = Depends(verify_token)):
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            # Query nodes
            nodes_result = session.run("MATCH (n) RETURN n LIMIT 2000")
            nodes = {}
            for record in nodes_result:
                n = record["n"]
                nodes[n.element_id] = {"id": n.element_id, "label": list(n.labels)[0], "properties": dict(n)}
                
            # Query relationships
            links_result = session.run("MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 5000")
            links = []
            for record in links_result:
                n = record["n"]
                m = record["m"]
                r = record["r"]
                
                n_id = n.element_id
                m_id = m.element_id
                
                if n_id not in nodes:
                    nodes[n_id] = {"id": n_id, "label": list(n.labels)[0], "properties": dict(n)}
                if m_id not in nodes:
                    nodes[m_id] = {"id": m_id, "label": list(m.labels)[0], "properties": dict(m)}
                    
                links.append({
                    "source": n_id,
                    "target": m_id,
                    "type": r.type,
                    "properties": dict(r)
                })
                
        driver.close()
        return {"nodes": list(nodes.values()), "links": links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
