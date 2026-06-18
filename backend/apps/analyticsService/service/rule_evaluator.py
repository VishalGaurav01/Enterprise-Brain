from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from uuid import UUID

from apps.employeeService.model.employee import Employee
from apps.employeeService.model.department import Department
from apps.projectService.model.project import Project
from apps.projectService.model.cost import ProjectCost
from apps.financeService.model.revenue import ProjectRevenue
from apps.employeeService.model.software_tool import SoftwareTool
from apps.financeService.model.reimbursement import Reimbursement

def get_department_roi(db: Session, department_id: UUID) -> float:
    # Revenue: sum(project_revenue) for projects in department
    rev = db.query(func.sum(ProjectRevenue.revenue_amount))\
        .join(Project, Project.id == ProjectRevenue.project_id)\
        .filter(Project.department_id == department_id).scalar() or 0.0

    # Costs: project_cost + software_tool + (assuming reimbursements map to department employees)
    pc = db.query(func.sum(ProjectCost.amount))\
        .join(Project, Project.id == ProjectCost.project_id)\
        .filter(Project.department_id == department_id).scalar() or 0.0

    st = db.query(func.sum(SoftwareTool.annual_cost))\
        .filter(SoftwareTool.department_id == department_id).scalar() or 0.0

    rem = db.query(func.sum(Reimbursement.claim_amount))\
        .join(Employee, Employee.id == Reimbursement.employee_id)\
        .filter(Employee.department_id == department_id).scalar() or 0.0

    total_inv = float(pc + st + rem)
    rev = float(rev)

    if total_inv == 0:
        return 0.0
    return ((rev - total_inv) / total_inv) * 100.0

def get_employee_roi(db: Session, employee_id: UUID) -> float:
    # Just a placeholder for employee ROI logic using similar aggregations
    return 150.0

def get_project_health(db: Session, project_id: UUID) -> float:
    # Placeholder for project health logic
    return 85.0

def get_org_metrics_details(db: Session) -> Dict[str, float]:
    rev = db.query(func.sum(ProjectRevenue.revenue_amount)).scalar() or 0.0
    pc = db.query(func.sum(ProjectCost.amount)).scalar() or 0.0
    st = db.query(func.sum(SoftwareTool.annual_cost)).scalar() or 0.0
    rem = db.query(func.sum(Reimbursement.claim_amount)).scalar() or 0.0
    # Add dummy salary for now or query employees
    salary = 500000.0 # dummy

    total_inv = float(pc) + float(st) + float(rem) + salary
    margin = float(rev) - total_inv

    return {
        "Total_Revenue": float(rev),
        "Total_Investment": total_inv,
        "Total_Project_Costs": float(pc),
        "Total_Tools_Cost": float(st),
        "Total_Reimbursements": float(rem),
        "Total_Salary": salary,
        "Margin": margin,
        "organization_margin": (margin / total_inv * 100) if total_inv else 0.0
    }

def get_cost_leakage(db: Session) -> float:
    return 15.0 # Placeholder leakage percentage

def get_entity_metrics(db: Session, entity_type: str, entity_id: UUID = None, is_organization: bool = False) -> Dict[str, Any]:
    metrics = {}
    if entity_type == 'department' and entity_id:
        metrics['department_roi'] = get_department_roi(db, entity_id)
        # Also map it to department_profit for UI backwards compatibility if needed
        metrics['department_profit'] = metrics['department_roi']
    elif entity_type == 'employee' and entity_id:
        metrics['employee_roi'] = get_employee_roi(db, entity_id)
        metrics['employee_utilization'] = 80.0
    elif entity_type == 'project' and entity_id:
        metrics['project_health'] = get_project_health(db, entity_id)
        metrics['project_roi'] = 20.0
        metrics['project_margin'] = 15.0
    elif entity_type == 'organization' or is_organization:
        org_metrics = get_org_metrics_details(db)
        metrics.update(org_metrics)
        metrics['cost_leakage'] = get_cost_leakage(db)
    
    return metrics
