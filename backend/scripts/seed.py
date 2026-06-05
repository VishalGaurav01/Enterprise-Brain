"""
seed.py — Population script for the Brain Enterprise Platform
Inserts realistic sample data respecting all FK relationships.

Run from backend/ directory:
    python scripts/seed.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from datetime import datetime, date
from decimal import Decimal

from bcrypt import hashpw, gensalt
from sqlalchemy.orm import Session

from core.config import SessionLocal

# ── Models ──────────────────────────────────────────────────────────────────
from apps.authService.model.auth              import User, Role, Permission
from apps.employeeService.model.employee      import Employee
from apps.employeeService.model.department    import Department
from apps.employeeService.model.designation   import Designation
from apps.employeeService.model.software_tool import SoftwareTool
from apps.projectService.model.project        import Project
from apps.projectService.model.assignment     import EmployeeProjectAssignment
from apps.projectService.model.vendor         import Vendor
from apps.projectService.model.cost           import ProjectCost
from apps.financeService.model.client         import Client
from apps.financeService.model.invoice        import Invoice
from apps.financeService.model.revenue        import ProjectRevenue
from apps.financeService.model.reimbursement  import Reimbursement


# ── Helpers ──────────────────────────────────────────────────────────────────
def uid() -> uuid.UUID:
    return uuid.uuid4()

def hashed(password: str) -> str:
    return hashpw(password.encode(), gensalt()).decode()

def d(year, month, day) -> date:
    return date(year, month, day)


# ── Seed ─────────────────────────────────────────────────────────────────────
def seed(db: Session):
    print("\n🌱  Starting seed...\n")

    # ── 1. PERMISSIONS ────────────────────────────────────────────────────────
    print("  [1/13] Permissions...")
    perms = {}
    for name, code in [
        ("View Employees",  "CAN_VIEW_EMPLOYEE"),
        ("Edit Employees",  "CAN_EDIT_EMPLOYEE"),
        ("View Projects",   "CAN_VIEW_PROJECT"),
        ("Manage Projects", "CAN_MANAGE_PROJECT"),
        ("View Finance",    "CAN_VIEW_FINANCE"),
        ("Manage Finance",  "CAN_MANAGE_FINANCE"),
        ("Admin Panel",     "CAN_ACCESS_ADMIN"),
    ]:
        p = Permission(id=uid(), name=name, code=code)
        db.add(p)
        perms[code] = p
    db.flush()

    # ── 2. ROLES ──────────────────────────────────────────────────────────────
    print("  [2/13] Roles...")
    role_admin = Role(id=uid(), name="Admin",   description="Full system access")
    role_pm    = Role(id=uid(), name="PM",      description="Project Manager")
    role_hr    = Role(id=uid(), name="HR",      description="Human Resources")
    role_fin   = Role(id=uid(), name="Finance", description="Finance team")
    role_dev   = Role(id=uid(), name="Dev",     description="Developer")

    role_admin.permissions = list(perms.values())
    role_pm.permissions    = [perms["CAN_VIEW_EMPLOYEE"], perms["CAN_VIEW_PROJECT"], perms["CAN_MANAGE_PROJECT"]]
    role_hr.permissions    = [perms["CAN_VIEW_EMPLOYEE"], perms["CAN_EDIT_EMPLOYEE"]]
    role_fin.permissions   = [perms["CAN_VIEW_FINANCE"],  perms["CAN_MANAGE_FINANCE"]]
    role_dev.permissions   = [perms["CAN_VIEW_PROJECT"]]

    for r in [role_admin, role_pm, role_hr, role_fin, role_dev]:
        db.add(r)
    db.flush()

    # ── 3. USERS ──────────────────────────────────────────────────────────────
    print("  [3/13] Users...")
    u_admin = User(id=uid(), username="admin",     email="admin@brain.io",  hashed_password=hashed("Admin@123"),  is_superuser=True,  status="active")
    u_pm    = User(id=uid(), username="pm_sarah",  email="sarah@brain.io",  hashed_password=hashed("Sarah@123"),  is_superuser=False, status="active")
    u_hr    = User(id=uid(), username="hr_james",  email="james@brain.io",  hashed_password=hashed("James@123"),  is_superuser=False, status="active")
    u_fin   = User(id=uid(), username="fin_maya",  email="maya@brain.io",   hashed_password=hashed("Maya@123"),   is_superuser=False, status="active")
    u_dev1  = User(id=uid(), username="dev_alex",  email="alex@brain.io",   hashed_password=hashed("Alex@123"),   is_superuser=False, status="active")
    u_dev2  = User(id=uid(), username="dev_priya", email="priya@brain.io",  hashed_password=hashed("Priya@123"),  is_superuser=False, status="active")

    u_admin.roles = [role_admin]
    u_pm.roles    = [role_pm]
    u_hr.roles    = [role_hr]
    u_fin.roles   = [role_fin]
    u_dev1.roles  = [role_dev]
    u_dev2.roles  = [role_dev]

    for u in [u_admin, u_pm, u_hr, u_fin, u_dev1, u_dev2]:
        db.add(u)
    db.flush()

    # ── 4. DESIGNATIONS ───────────────────────────────────────────────────────
    print("  [4/13] Designations...")
    des_cto    = Designation(id=uid(), name="CTO",               description="Chief Technology Officer", grade="L10", pay_band="30L-50L",  status="active", created_by=u_admin.id)
    des_pm     = Designation(id=uid(), name="Project Manager",   description="Manages projects",         grade="L7",  pay_band="15L-25L",  status="active", created_by=u_admin.id)
    des_se     = Designation(id=uid(), name="Software Engineer", description="Writes code",              grade="L4",  pay_band="8L-14L",   status="active", created_by=u_admin.id)
    des_hr_mgr = Designation(id=uid(), name="HR Manager",        description="Manages HR ops",           grade="L6",  pay_band="10L-18L",  status="active", created_by=u_admin.id)
    des_fin_an = Designation(id=uid(), name="Finance Analyst",   description="Manages finances",         grade="L5",  pay_band="9L-15L",   status="active", created_by=u_admin.id)

    for des in [des_cto, des_pm, des_se, des_hr_mgr, des_fin_an]:
        db.add(des)
    db.flush()

    # ── 5. DEPARTMENTS (heads assigned after employees exist) ─────────────────
    print("  [5/13] Departments...")
    dept_eng = Department(id=uid(), name="Engineering", description="Product engineering", status="active", cost_center_code="CC-ENG-01", created_by=u_admin.id)
    dept_hr  = Department(id=uid(), name="HR",          description="Human Resources",    status="active", cost_center_code="CC-HR-01",  created_by=u_admin.id)
    dept_fin = Department(id=uid(), name="Finance",     description="Finance & Accounts", status="active", cost_center_code="CC-FIN-01", created_by=u_admin.id)
    dept_pm  = Department(id=uid(), name="PMO",         description="Project Management", status="active", cost_center_code="CC-PMO-01", created_by=u_admin.id)

    for dep in [dept_eng, dept_hr, dept_fin, dept_pm]:
        db.add(dep)
    db.flush()

    # ── 6. EMPLOYEES ──────────────────────────────────────────────────────────
    print("  [6/13] Employees...")
    emp_cto  = Employee(id=uid(), user_code="EMP-001", first_name="Rahul", last_name="Sharma", email="rahul.sharma@brain.io", contact_number="+91-9000000001", department_id=dept_eng.id, designation_id=des_cto.id,    manager_id=None, status="active", created_by=u_admin.id)
    emp_pm   = Employee(id=uid(), user_code="EMP-002", first_name="Sarah", last_name="Connor", email="sarah.connor@brain.io", contact_number="+91-9000000002", department_id=dept_pm.id,  designation_id=des_pm.id,     manager_id=None, status="active", created_by=u_admin.id)
    emp_hr   = Employee(id=uid(), user_code="EMP-003", first_name="James", last_name="Wright", email="james.wright@brain.io", contact_number="+91-9000000003", department_id=dept_hr.id,  designation_id=des_hr_mgr.id, manager_id=None, status="active", created_by=u_admin.id)
    emp_fin  = Employee(id=uid(), user_code="EMP-004", first_name="Maya",  last_name="Patel",  email="maya.patel@brain.io",   contact_number="+91-9000000004", department_id=dept_fin.id, designation_id=des_fin_an.id, manager_id=None, status="active", created_by=u_admin.id)
    emp_dev1 = Employee(id=uid(), user_code="EMP-005", first_name="Alex",  last_name="Turner", email="alex.turner@brain.io",  contact_number="+91-9000000005", department_id=dept_eng.id, designation_id=des_se.id,     manager_id=None, status="active", created_by=u_admin.id)
    emp_dev2 = Employee(id=uid(), user_code="EMP-006", first_name="Priya", last_name="Singh",  email="priya.singh@brain.io",  contact_number="+91-9000000006", department_id=dept_eng.id, designation_id=des_se.id,     manager_id=None, status="active", created_by=u_admin.id)

    for emp in [emp_cto, emp_pm, emp_hr, emp_fin, emp_dev1, emp_dev2]:
        db.add(emp)
    db.flush()

    # Set manager hierarchy and department heads
    emp_pm.manager_id   = emp_cto.id
    emp_dev1.manager_id = emp_cto.id
    emp_dev2.manager_id = emp_cto.id
    emp_hr.manager_id   = emp_cto.id
    emp_fin.manager_id  = emp_cto.id

    dept_eng.head_employee_id = emp_cto.id
    dept_pm.head_employee_id  = emp_pm.id
    dept_hr.head_employee_id  = emp_hr.id
    dept_fin.head_employee_id = emp_fin.id
    db.flush()

    # ── 7. SOFTWARE TOOLS ─────────────────────────────────────────────────────
    print("  [7/13] Software Tools...")
    for name, dept, cost in [
        ("Jira Premium",       dept_pm.id,  "48000.00"),
        ("GitHub Enterprise",  dept_eng.id, "84000.00"),
        ("Figma Organization", dept_eng.id, "36000.00"),
        ("QuickBooks",         dept_fin.id, "24000.00"),
        ("BambooHR",           dept_hr.id,  "30000.00"),
    ]:
        db.add(SoftwareTool(id=uid(), name=name, department_id=dept, annual_cost=Decimal(cost), created_by=u_admin.id))
    db.flush()

    # ── 8. CLIENTS ────────────────────────────────────────────────────────────
    print("  [8/13] Clients...")
    client_acme = Client(id=uid(), company_name="Acme Corp",      industry="Retail",     created_by=u_admin.id)
    client_nova = Client(id=uid(), company_name="Nova Systems",   industry="Technology", created_by=u_admin.id)
    client_peak = Client(id=uid(), company_name="Peak Analytics", industry="Analytics",  created_by=u_admin.id)

    for c in [client_acme, client_nova, client_peak]:
        db.add(c)
    db.flush()

    # ── 9. PROJECTS ───────────────────────────────────────────────────────────
    print("  [9/13] Projects...")
    proj_alpha = Project(id=uid(), name="Project Alpha", project_type="fixed-price",       department_id=dept_eng.id, owner_employee_id=emp_pm.id,  client_id=client_acme.id, budget_allocated=Decimal("500000.00"), status="active",   start_date=d(2026,1,1), end_date=d(2026,12,31), created_by=u_admin.id)
    proj_beta  = Project(id=uid(), name="Project Beta",  project_type="time-and-material", department_id=dept_eng.id, owner_employee_id=emp_pm.id,  client_id=client_nova.id, budget_allocated=Decimal("750000.00"), status="active",   start_date=d(2026,2,1), end_date=d(2026,9,30),  created_by=u_admin.id)
    proj_gamma = Project(id=uid(), name="Project Gamma", project_type="retainer",          department_id=dept_pm.id,  owner_employee_id=emp_cto.id, client_id=client_peak.id, budget_allocated=Decimal("200000.00"), status="planning", start_date=d(2026,4,1), end_date=d(2026,10,31), created_by=u_admin.id)

    for p in [proj_alpha, proj_beta, proj_gamma]:
        db.add(p)
    db.flush()

    # ── 10. ASSIGNMENTS ───────────────────────────────────────────────────────
    print("  [10/13] Assignments...")
    for emp, proj, role, alloc, rate, sd, ed in [
        (emp_dev1, proj_alpha, "Lead Developer",  "80", "5000", d(2026,1,1),  d(2026,12,31)),
        (emp_dev2, proj_alpha, "Developer",       "60", "4000", d(2026,1,1),  d(2026,12,31)),
        (emp_dev1, proj_beta,  "Developer",       "20", "4500", d(2026,2,1),  d(2026,9,30)),
        (emp_dev2, proj_beta,  "Lead Developer",  "40", "5500", d(2026,2,1),  d(2026,9,30)),
        (emp_pm,   proj_gamma, "Project Manager", "50", "7000", d(2026,4,1),  d(2026,10,31)),
    ]:
        db.add(EmployeeProjectAssignment(id=uid(), employee_id=emp.id, project_id=proj.id, role=role, allocation_percent=Decimal(alloc), billing_rate=Decimal(rate), start_date=sd, end_date=ed, contribution_type="billable", created_by=u_admin.id))
    db.flush()

    # ── 11. VENDORS & PROJECT COSTS ───────────────────────────────────────────
    print("  [11/13] Vendors & Project Costs...")
    vendor_aws = Vendor(id=uid(), name="Amazon Web Services", service_type="Cloud Hosting",  created_by=u_admin.id)
    vendor_ui  = Vendor(id=uid(), name="UX Studio",           service_type="Design",         created_by=u_admin.id)
    vendor_sec = Vendor(id=uid(), name="SecureShield",        service_type="Security Audit", created_by=u_admin.id)

    for v in [vendor_aws, vendor_ui, vendor_sec]:
        db.add(v)
    db.flush()

    for proj, vendor, amount, cost_type, expense_date in [
        (proj_alpha, vendor_aws, "25000.00", "infrastructure", d(2026,1,15)),
        (proj_alpha, vendor_ui,  "18000.00", "design",         d(2026,2,10)),
        (proj_beta,  vendor_aws, "32000.00", "infrastructure", d(2026,2,20)),
        (proj_beta,  vendor_sec, "15000.00", "security",       d(2026,3,5)),
        (proj_gamma, vendor_aws, "10000.00", "infrastructure", d(2026,4,12)),
    ]:
        db.add(ProjectCost(id=uid(), project_id=proj.id, vendor_id=vendor.id, amount=Decimal(amount), cost_type=cost_type, expense_date=expense_date, created_by=u_admin.id))
    db.flush()

    # ── 12. INVOICES & PROJECT REVENUE ────────────────────────────────────────
    print("  [12/13] Invoices & Revenue...")
    inv1 = Invoice(id=uid(), client_id=client_acme.id, project_id=proj_alpha.id, amount=Decimal("150000.00"), due_date=d(2026,3,31), created_by=u_admin.id)
    inv2 = Invoice(id=uid(), client_id=client_nova.id, project_id=proj_beta.id,  amount=Decimal("200000.00"), due_date=d(2026,4,30), created_by=u_admin.id)
    inv3 = Invoice(id=uid(), client_id=client_acme.id, project_id=proj_alpha.id, amount=Decimal("100000.00"), due_date=d(2026,6,30), created_by=u_admin.id)
    inv4 = Invoice(id=uid(), client_id=client_peak.id, project_id=proj_gamma.id, amount=Decimal("75000.00"),  due_date=d(2026,5,31), created_by=u_admin.id)

    for inv in [inv1, inv2, inv3, inv4]:
        db.add(inv)
    db.flush()

    for proj, client, inv, amount, rec_date in [
        (proj_alpha, client_acme, inv1, "140000.00", d(2026,3,31)),
        (proj_beta,  client_nova, inv2, "190000.00", d(2026,4,30)),
        (proj_alpha, client_acme, inv3, "95000.00",  d(2026,6,30)),
        (proj_gamma, client_peak, inv4, "70000.00",  d(2026,5,31)),
    ]:
        db.add(ProjectRevenue(id=uid(), project_id=proj.id, client_id=client.id, invoice_id=inv.id, revenue_amount=Decimal(amount), recognized_date=rec_date, created_by=u_admin.id))
    db.flush()

    # ── 13. REIMBURSEMENTS ────────────────────────────────────────────────────
    print("  [13/13] Reimbursements...")
    for emp, amount, status, desc, created_by in [
        (emp_dev1, "4500.00", "approved", "Flight to client site - Acme Corp",  u_admin.id),
        (emp_dev2, "1200.00", "approved", "Team lunch - project kickoff",        u_admin.id),
        (emp_pm,   "8000.00", "pending",  "Hotel stay - Nova Systems visit",     u_pm.id),
        (emp_hr,   "2500.00", "pending",  "HR conference registration fee",      u_hr.id),
        (emp_fin,  "3000.00", "rejected", "Duplicate claim - travel expense",    u_fin.id),
    ]:
        db.add(Reimbursement(id=uid(), employee_id=emp.id, expense_id=uid(), claim_amount=Decimal(amount), status=status, description=desc, created_by=created_by))
    db.flush()

    db.commit()

    print("\n✅  Seed complete! Summary:")
    print("     Permissions    : 7")
    print("     Roles          : 5")
    print("     Users          : 6")
    print("     Designations   : 5")
    print("     Departments    : 4")
    print("     Employees      : 6")
    print("     Software Tools : 5")
    print("     Clients        : 3")
    print("     Projects       : 3")
    print("     Assignments    : 5")
    print("     Vendors        : 3")
    print("     Project Costs  : 5")
    print("     Invoices       : 4")
    print("     Project Revenue: 4")
    print("     Reimbursements : 5")
    print("     Total          : 70 records\n")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    except Exception as e:
        db.rollback()
        print(f"\n❌  Seed failed: {e}")
        raise
    finally:
        db.close()
