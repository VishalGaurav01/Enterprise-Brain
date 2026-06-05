# pyrefly: ignore [missing-import]
import simpleeval
from sqlalchemy.orm import Session
from uuid import UUID
from apps.analyticsService.model.rule_engine import RuleEngineConfig
from apps.employeeService.model.employee import Employee
from apps.employeeService.model.department import Department
from apps.employeeService.model.software_tool import SoftwareTool
from apps.projectService.model.project import Project
from apps.projectService.model.assignment import EmployeeProjectAssignment
from apps.financeService.model.revenue import ProjectRevenue
from apps.projectService.model.cost import ProjectCost
from apps.financeService.model.reimbursement import Reimbursement
from apps.employeeService.model.designation import Designation
from decimal import Decimal

def _get_employee_salary(db: Session, employee_id: UUID) -> float:
    """Helper to extract rough salary from designation."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee: return 0.0
    designation = db.query(Designation).filter(Designation.id == employee.designation_id).first()
    if designation and designation.pay_band:
        try:
            return float(designation.pay_band.split('-')[0].replace('L', '00000').replace('₹', '').replace(' ', ''))
        except:
            pass
    return 0.0

def get_employee_context(db: Session, employee_id: UUID) -> dict:
    """Gathers data related to an employee for rule evaluation."""
    salary = _get_employee_salary(db, employee_id)

    reimbursements = db.query(Reimbursement).filter(
        Reimbursement.employee_id == employee_id,
        Reimbursement.status == 'approved'
    ).all()
    total_reimbursements = sum([float(r.claim_amount) for r in reimbursements])

    assignments = db.query(EmployeeProjectAssignment).filter(
        EmployeeProjectAssignment.employee_id == employee_id
    ).all()
    
    attributed_revenue = 0.0
    billable_hours = 0.0
    total_allocated_hours = 0.0

    for assign in assignments:
        project_revenues = db.query(ProjectRevenue).filter(
            ProjectRevenue.project_id == assign.project_id
        ).all()
        total_proj_rev = sum([float(r.revenue_amount) for r in project_revenues])
        
        alloc_percent = float(assign.allocation_percent or 0) / 100.0
        attributed_revenue += total_proj_rev * alloc_percent
        
        alloc_hours = 160 * alloc_percent
        total_allocated_hours += 160
        if assign.contribution_type == 'billable':
            billable_hours += alloc_hours

    total_investment = salary + total_reimbursements
    if total_investment == 0: total_investment = 1.0 
    
    utilization = (billable_hours / total_allocated_hours * 100) if total_allocated_hours > 0 else 0.0

    return {
        "Attributed_Revenue": attributed_revenue,
        "Total_Investment": total_investment,
        "Salary": salary,
        "Total_Reimbursements": total_reimbursements,
        "Billable_Hours": billable_hours,
        "Allocated_Hours": total_allocated_hours,
        "Utilization": utilization
    }

def get_project_context(db: Session, project_id: UUID) -> dict:
    """Gathers data related to a project for rule evaluation."""
    revenues = db.query(ProjectRevenue).filter(ProjectRevenue.project_id == project_id).all()
    total_revenue = sum([float(r.revenue_amount) for r in revenues])

    vendor_costs = db.query(ProjectCost).filter(ProjectCost.project_id == project_id).all()
    total_vendor_cost = sum([float(c.amount) for c in vendor_costs])

    assignments = db.query(EmployeeProjectAssignment).filter(EmployeeProjectAssignment.project_id == project_id).all()
    employee_allocated_cost = 0.0
    for assign in assignments:
        emp_salary = _get_employee_salary(db, assign.employee_id)
        alloc_percent = float(assign.allocation_percent or 0) / 100.0
        employee_allocated_cost += (emp_salary * alloc_percent)

    total_investment = total_vendor_cost + employee_allocated_cost
    if total_investment == 0: total_investment = 1.0

    return {
        "Total_Revenue": total_revenue,
        "Total_Investment": total_investment,
        "Vendor_Costs": total_vendor_cost,
        "Employee_Costs": employee_allocated_cost,
        "Margin": total_revenue - total_investment
    }

def get_department_context(db: Session, department_id: UUID) -> dict:
    """Gathers data related to a department for rule evaluation."""
    projects = db.query(Project).filter(Project.department_id == department_id).all()
    total_revenue = 0.0
    total_project_cost = 0.0
    for proj in projects:
        revenues = db.query(ProjectRevenue).filter(ProjectRevenue.project_id == proj.id).all()
        total_revenue += sum([float(r.revenue_amount) for r in revenues])
        costs = db.query(ProjectCost).filter(ProjectCost.project_id == proj.id).all()
        total_project_cost += sum([float(c.amount) for c in costs])

    employees = db.query(Employee).filter(Employee.department_id == department_id).all()
    total_salary = 0.0
    total_reimbursements = 0.0
    for emp in employees:
        total_salary += _get_employee_salary(db, emp.id)
        reimbs = db.query(Reimbursement).filter(Reimbursement.employee_id == emp.id, Reimbursement.status == 'approved').all()
        total_reimbursements += sum([float(r.claim_amount) for r in reimbs])

    tools = db.query(SoftwareTool).filter(SoftwareTool.department_id == department_id).all()
    total_tools_cost = sum([float(t.annual_cost) for t in tools])

    total_investment = total_salary + total_reimbursements + total_project_cost + total_tools_cost
    if total_investment == 0: total_investment = 1.0

    return {
        "Total_Revenue": total_revenue,
        "Total_Investment": total_investment,
        "Total_Salary": total_salary,
        "Total_Tools_Cost": total_tools_cost,
        "Total_Project_Costs": total_project_cost,
        "Profit": total_revenue - total_investment
    }

def get_organization_context(db: Session) -> dict:
    """Gathers data for the entire organization for rule evaluation."""
    revenues = db.query(ProjectRevenue).all()
    total_revenue = sum([float(r.revenue_amount) for r in revenues])

    employees = db.query(Employee).all()
    total_salary = sum([_get_employee_salary(db, emp.id) for emp in employees])

    tools = db.query(SoftwareTool).all()
    total_tools_cost = sum([float(t.annual_cost) for t in tools])

    proj_costs = db.query(ProjectCost).all()
    total_project_cost = sum([float(c.amount) for c in proj_costs])

    reimbs = db.query(Reimbursement).filter(Reimbursement.status == 'approved').all()
    total_reimbursements = sum([float(r.claim_amount) for r in reimbs])

    total_investment = total_salary + total_reimbursements + total_project_cost + total_tools_cost
    if total_investment == 0: total_investment = 1.0

    return {
        "Total_Revenue": total_revenue,
        "Total_Investment": total_investment,
        "Total_Salary": total_salary,
        "Total_Tools_Cost": total_tools_cost,
        "Total_Project_Costs": total_project_cost,
        "Total_Reimbursements": total_reimbursements,
        "Margin": total_revenue - total_investment
    }

def evaluate_rule(
    db: Session, 
    rule_expression: str, 
    employee_id: UUID = None, 
    project_id: UUID = None,
    department_id: UUID = None,
    is_organization: bool = False
) -> float:
    """Evaluates a mathematical string rule using simpleeval."""
    variables = {}
    
    if employee_id:
        variables.update(get_employee_context(db, employee_id))
    elif project_id:
        variables.update(get_project_context(db, project_id))
    elif department_id:
        variables.update(get_department_context(db, department_id))
    elif is_organization:
        variables.update(get_organization_context(db))
        
    try:
        result = simpleeval.simple_eval(rule_expression, names=variables)
        return float(result)
    except Exception as e:
        raise ValueError(f"Rule evaluation failed: {str(e)}")
