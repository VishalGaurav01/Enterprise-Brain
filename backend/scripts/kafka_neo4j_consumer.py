import os
import json
import logging
import time
from kafka import KafkaConsumer
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_SERVERS = os.getenv("KAFKA_SERVERS", "kafka:9092")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def get_kafka_consumer():
    while True:
        try:
            consumer = KafkaConsumer(
                'db.events',
                bootstrap_servers=KAFKA_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='neo4j-sync-group',
                auto_offset_reset='earliest'
            )
            return consumer
        except Exception as e:
            logger.error(f"Kafka connection failed, retrying... ({e})")
            time.sleep(5)

def process_message(session, message):
    event_type = message.get("event_type")
    payload = message.get("data", {})
    operation = payload.get("operation")
    table = payload.get("table")
    data = payload.get("data", {})
    
    if not all([operation, table, data, data.get("id")]):
        return

    node_id = data.get("id")

    # Determine Label
    label_map = {
        "departments": "Department",
        "clients": "Client",
        "vendors": "Vendor",
        "employees": "Employee",
        "projects": "Project",
        "assignments": "EmployeeProjectAssignment",
        "invoices": "Invoice",
        "project_costs": "ProjectCost",
        "project_revenues": "ProjectRevenue"
    }
    
    label = label_map.get(table)
    if not label:
        return

    if operation == "delete":
        session.run(f"MATCH (n:{label} {{id: $id}}) DETACH DELETE n", id=node_id)
        logger.info(f"Deleted {label} {node_id}")
        return

    # For insert and update, we UPSERT (MERGE) the node
    set_clause = ", ".join([f"n.{k} = ${k}" for k in data.keys() if data[k] is not None])
    merge_query = f"""
    MERGE (n:{label} {{id: $id}})
    SET {set_clause}
    """
    # Create the node properties
    session.run(merge_query, **data)
    logger.info(f"Upserted {label} {node_id}")

    # Process Relationships based on table
    if table == "employees" and data.get("department_id"):
        session.run(
            """
            MATCH (e:Employee {id: $emp_id})
            MATCH (d:Department {id: $dept_id})
            MERGE (e)-[:WORKS_IN]->(d)
            """,
            emp_id=node_id, dept_id=data["department_id"]
        )
    elif table == "projects":
        if data.get("department_id"):
            session.run("MATCH (p:Project {id: $p_id}), (d:Department {id: $d_id}) MERGE (p)-[:BELONGS_TO]->(d)", p_id=node_id, d_id=data["department_id"])
        if data.get("owner_employee_id"):
            session.run("MATCH (p:Project {id: $p_id}), (e:Employee {id: $e_id}) MERGE (e)-[:OWNS]->(p)", p_id=node_id, e_id=data["owner_employee_id"])
        if data.get("client_id"):
            session.run("MATCH (p:Project {id: $p_id}), (c:Client {id: $c_id}) MERGE (p)-[:SPONSORED_BY]->(c)", p_id=node_id, c_id=data["client_id"])
    elif table == "assignments":
        session.run(
            """
            MATCH (e:Employee {id: $e_id}), (p:Project {id: $p_id})
            MERGE (e)-[r:ASSIGNED_TO]->(p)
            SET r.role = $role, r.allocation = $allocation
            """,
            e_id=data.get("employee_id"), p_id=data.get("project_id"), 
            role=data.get("role"), allocation=data.get("allocation_percent", 0.0)
        )
    elif table == "invoices":
        session.run("MATCH (i:Invoice {id: $i_id}), (c:Client {id: $c_id}) MERGE (c)-[:RECEIVED_INVOICE]->(i)", i_id=node_id, c_id=data.get("client_id"))
        session.run("MATCH (i:Invoice {id: $i_id}), (p:Project {id: $p_id}) MERGE (i)-[:BILLED_TO]->(p)", i_id=node_id, p_id=data.get("project_id"))
    elif table == "project_costs":
        session.run("MATCH (pc:ProjectCost {id: $pc_id}), (p:Project {id: $p_id}) MERGE (p)-[:HAS_COST]->(pc)", pc_id=node_id, p_id=data.get("project_id"))
        session.run("MATCH (pc:ProjectCost {id: $pc_id}), (v:Vendor {id: $v_id}) MERGE (pc)-[:PAID_TO]->(v)", pc_id=node_id, v_id=data.get("vendor_id"))
    elif table == "project_revenues":
        session.run("MATCH (pr:ProjectRevenue {id: $pr_id}), (p:Project {id: $p_id}) MERGE (p)-[:GENERATED_REVENUE]->(pr)", pr_id=node_id, p_id=data.get("project_id"))
        session.run("MATCH (pr:ProjectRevenue {id: $pr_id}), (c:Client {id: $c_id}) MERGE (c)-[:PAID_REVENUE]->(pr)", pr_id=node_id, c_id=data.get("client_id"))


def run_worker():
    logger.info("Starting Kafka to Neo4j Sync Worker...")
    consumer = get_kafka_consumer()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    logger.info("Successfully connected to Kafka and Neo4j. Listening for events...")
    
    with driver.session() as session:
        for message in consumer:
            try:
                process_message(session, message.value)
            except Exception as e:
                logger.error(f"Error processing message: {e}")

if __name__ == "__main__":
    run_worker()
