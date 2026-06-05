import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from apps.analyticsService.model.rule_engine import RuleEngineConfig
from apps.analyticsService.service.rule_evaluator import evaluate_rule, get_employee_context, get_project_context, get_department_context, get_organization_context
from apps.employeeService.model.employee import Employee
from apps.projectService.model.project import Project
from apps.employeeService.model.department import Department
import uuid

def test_rule_engine():
    db = SessionLocal()
    try:
        print("1. Creating test rules...")
        
        # Rule 1: Employee ROI
        roi_rule = db.query(RuleEngineConfig).filter(RuleEngineConfig.rule_name == 'employee_roi_v1').first()
        if not roi_rule:
            db.add(RuleEngineConfig(id=uuid.uuid4(), rule_name='employee_roi_v1', expression='((Attributed_Revenue - Total_Investment) / Total_Investment) * 100', description='Calculates ROI percentage for an employee'))
            
        # Rule 2: Utilization
        util_rule = db.query(RuleEngineConfig).filter(RuleEngineConfig.rule_name == 'employee_utilization_v1').first()
        if not util_rule:
            db.add(RuleEngineConfig(id=uuid.uuid4(), rule_name='employee_utilization_v1', expression='Utilization', description='Calculates utilization percentage'))
            
        # Rule 3: Project ROI
        proj_roi_rule = db.query(RuleEngineConfig).filter(RuleEngineConfig.rule_name == 'project_roi_v1').first()
        if not proj_roi_rule:
            db.add(RuleEngineConfig(id=uuid.uuid4(), rule_name='project_roi_v1', expression='((Total_Revenue - Total_Investment) / Total_Investment) * 100', description='Calculates Project ROI'))

        # Rule 4: Department Profit
        dept_profit_rule = db.query(RuleEngineConfig).filter(RuleEngineConfig.rule_name == 'department_profit_v1').first()
        if not dept_profit_rule:
            db.add(RuleEngineConfig(id=uuid.uuid4(), rule_name='department_profit_v1', expression='Total_Revenue - Total_Investment', description='Calculates Department Profit'))

        # Rule 5: Org Margin
        org_margin_rule = db.query(RuleEngineConfig).filter(RuleEngineConfig.rule_name == 'org_margin_v1').first()
        if not org_margin_rule:
            db.add(RuleEngineConfig(id=uuid.uuid4(), rule_name='org_margin_v1', expression='Total_Revenue - Total_Investment', description='Calculates Org Margin'))

        db.commit()
        print("Rules created successfully.")
        
        # Test Evaluation
        print("\n2. Testing Evaluation...")
        
        # --- EMPLOYEE ---
        emp = db.query(Employee).filter(Employee.user_code == 'EMP-005').first()
        if emp:
            print(f"\nEvaluating for Employee: {emp.first_name} {emp.last_name}")
            print(f"Employee Context Variables: {get_employee_context(db, emp.id)}")
            print(f"Calculated ROI: {evaluate_rule(db, '((Attributed_Revenue - Total_Investment) / Total_Investment) * 100', employee_id=emp.id)}%")
            print(f"Calculated Utilization: {evaluate_rule(db, 'Utilization', employee_id=emp.id)}%")

        # --- PROJECT ---
        proj = db.query(Project).filter(Project.name == 'Project Alpha').first()
        if proj:
            print(f"\nEvaluating for Project: {proj.name}")
            print(f"Project Context Variables: {get_project_context(db, proj.id)}")
            print(f"Calculated Project ROI: {evaluate_rule(db, '((Total_Revenue - Total_Investment) / Total_Investment) * 100', project_id=proj.id)}%")

        # --- DEPARTMENT ---
        dept = db.query(Department).filter(Department.name == 'Engineering').first()
        if dept:
            print(f"\nEvaluating for Department: {dept.name}")
            print(f"Department Context Variables: {get_department_context(db, dept.id)}")
            print(f"Calculated Department Profit: {evaluate_rule(db, 'Total_Revenue - Total_Investment', department_id=dept.id)}")

        # --- ORGANIZATION ---
        print(f"\nEvaluating for Organization")
        print(f"Organization Context Variables: {get_organization_context(db)}")
        print(f"Calculated Org Margin: {evaluate_rule(db, 'Total_Revenue - Total_Investment', is_organization=True)}")
            
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_rule_engine()
