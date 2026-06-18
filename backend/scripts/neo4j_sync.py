import os
import sys
from neo4j import GraphDatabase

# Add backend directory to path so we can import apps and core
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config import SessionLocal
from apps.employeeService.model.employee import Employee
from apps.employeeService.model.department import Department
from apps.financeService.model.client import Client
from apps.financeService.model.invoice import Invoice
from apps.financeService.model.revenue import ProjectRevenue
from apps.projectService.model.cost import ProjectCost
from apps.projectService.model.vendor import Vendor
from apps.projectService.model.project import Project
from apps.projectService.model.assignment import EmployeeProjectAssignment

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def sync_to_neo4j():
    db = SessionLocal()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        # Fetch data from Postgres
        employees = db.query(Employee).all()
        departments = db.query(Department).all()
        projects = db.query(Project).all()
        assignments = db.query(EmployeeProjectAssignment).all()
        clients = db.query(Client).all()
        vendors = db.query(Vendor).all()
        invoices = db.query(Invoice).all()
        project_costs = db.query(ProjectCost).all()
        project_revenues = db.query(ProjectRevenue).all()
        
        with driver.session() as session:
            # Clear existing data (for full sync)
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create Departments
            for dept in departments:
                session.run(
                    "CREATE (d:Department {id: $id, name: $name, cost_center_code: $code})",
                    id=str(dept.id), name=dept.name, code=dept.cost_center_code
                )
                
            # Create Clients
            for client in clients:
                session.run(
                    "CREATE (c:Client {id: $id, name: $name, industry: $industry})",
                    id=str(client.id), name=client.company_name, industry=client.industry
                )
                
            # Create Vendors
            for vendor in vendors:
                session.run(
                    "CREATE (v:Vendor {id: $id, name: $name, service_type: $service_type})",
                    id=str(vendor.id), name=vendor.name, service_type=vendor.service_type
                )
            
            # Create Employees and their WORKS_IN relationship
            for emp in employees:
                session.run(
                    """
                    CREATE (e:Employee {id: $id, first_name: $first_name, last_name: $last_name, email: $email})
                    WITH e
                    MATCH (d:Department {id: $dept_id})
                    CREATE (e)-[:WORKS_IN]->(d)
                    """,
                    id=str(emp.id), first_name=emp.first_name, last_name=emp.last_name,
                    email=emp.email, dept_id=str(emp.department_id)
                )
            
            # Create Projects and BELONGS_TO department relationship
            for proj in projects:
                session.run(
                    """
                    CREATE (p:Project {id: $id, name: $name, type: $type, status: $status})
                    WITH p
                    MATCH (d:Department {id: $dept_id})
                    CREATE (p)-[:BELONGS_TO]->(d)
                    """,
                    id=str(proj.id), name=proj.name, type=proj.project_type,
                    status=proj.status, dept_id=str(proj.department_id)
                )
                
                # Owner relationship
                if proj.owner_employee_id:
                    session.run(
                        """
                        MATCH (p:Project {id: $proj_id})
                        MATCH (e:Employee {id: $emp_id})
                        CREATE (e)-[:OWNS]->(p)
                        """,
                        proj_id=str(proj.id), emp_id=str(proj.owner_employee_id)
                    )
                    
                # Client relationship
                if proj.client_id:
                    session.run(
                        """
                        MATCH (p:Project {id: $proj_id})
                        MATCH (c:Client {id: $client_id})
                        CREATE (p)-[:SPONSORED_BY]->(c)
                        """,
                        proj_id=str(proj.id), client_id=str(proj.client_id)
                    )

            # Create ASSIGNED_TO relationships
            for assignment in assignments:
                session.run(
                    """
                    MATCH (e:Employee {id: $emp_id})
                    MATCH (p:Project {id: $proj_id})
                    CREATE (e)-[:ASSIGNED_TO {role: $role, allocation: $allocation}]->(p)
                    """,
                    emp_id=str(assignment.employee_id), proj_id=str(assignment.project_id),
                    role=assignment.role, allocation=float(assignment.allocation_percent) if assignment.allocation_percent else 0.0
                )
                
            # Create Invoices
            for invoice in invoices:
                session.run(
                    """
                    MATCH (c:Client {id: $client_id})
                    MATCH (p:Project {id: $project_id})
                    CREATE (i:Invoice {id: $id, amount: $amount})
                    CREATE (c)-[:RECEIVED_INVOICE]->(i)
                    CREATE (i)-[:BILLED_TO]->(p)
                    """,
                    id=str(invoice.id), amount=float(invoice.amount) if invoice.amount else 0.0,
                    client_id=str(invoice.client_id), project_id=str(invoice.project_id)
                )

            # Create Project Costs
            for cost in project_costs:
                session.run(
                    """
                    MATCH (p:Project {id: $project_id})
                    MATCH (v:Vendor {id: $vendor_id})
                    CREATE (pc:ProjectCost {id: $id, amount: $amount, type: $type})
                    CREATE (p)-[:HAS_COST]->(pc)
                    CREATE (pc)-[:PAID_TO]->(v)
                    """,
                    id=str(cost.id), amount=float(cost.amount) if cost.amount else 0.0, type=cost.cost_type,
                    project_id=str(cost.project_id), vendor_id=str(cost.vendor_id)
                )

            # Create Project Revenues
            for revenue in project_revenues:
                session.run(
                    """
                    MATCH (p:Project {id: $project_id})
                    MATCH (c:Client {id: $client_id})
                    CREATE (pr:ProjectRevenue {id: $id, amount: $amount})
                    CREATE (p)-[:GENERATED_REVENUE]->(pr)
                    CREATE (c)-[:PAID_REVENUE]->(pr)
                    """,
                    id=str(revenue.id), amount=float(revenue.revenue_amount) if revenue.revenue_amount else 0.0,
                    project_id=str(revenue.project_id), client_id=str(revenue.client_id)
                )
                
        print("Successfully synced data to Neo4j")
    
    except Exception as e:
        print(f"Error syncing to Neo4j: {e}")
    finally:
        db.close()
        driver.close()

if __name__ == "__main__":
    sync_to_neo4j()
