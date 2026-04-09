import uuid
import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

# Adjust path because script is now in 'scripts/' subdirectory
# We move up ONE level to reach 'backend/' where 'apps' and 'core' live
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, engine
from core.config import Base
from apps.shared.security import get_password_hash

# Model Imports
from apps.authService.model.auth import User
from apps.employeeService.model.department import Department
from apps.employeeService.model.designation import Designation
from apps.employeeService.model.employee import Employee
from apps.projectService.model.client import Client
from apps.projectService.model.project import Project
from apps.projectService.model.vendor import Vendor
from apps.projectService.model.cost import ProjectCost
from apps.projectService.model.assignment import EmployeeProjectAssignment
from apps.projectService.model.invoice import Invoice
from apps.projectService.model.revenue import ProjectRevenue

def seed_data():
    db: Session = SessionLocal()
    try:
        print("--- Starting Database Seeding ---")

        # 1. Create Admin User
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                id=uuid.uuid4(),
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                is_active=True
            )
            db.add(admin_user)
            db.flush()
            print("Admin user created.")

        admin_id = admin_user.id

        # 2. Add Departments
        depts = [
            Department(id=uuid.uuid4(), name="Engineering", description="Core product development", created_by=admin_id),
            Department(id=uuid.uuid4(), name="Marketing", description="Brand and growth", created_by=admin_id),
            Department(id=uuid.uuid4(), name="Finance", description="Accounts and payroll", created_by=admin_id)
        ]
        db.add_all(depts)
        db.flush()
        print(f"Added {len(depts)} departments.")

        # 3. Add Designations
        designations = [
            Designation(id=uuid.uuid4(), name="Lead Engineer", created_by=admin_id),
            Designation(id=uuid.uuid4(), name="Designer", created_by=admin_id),
            Designation(id=uuid.uuid4(), name="Product Manager", created_by=admin_id)
        ]
        db.add_all(designations)
        db.flush()
        print(f"Added {len(designations)} designations.")

        # 4. Add Employees
        emp = Employee(
            id=uuid.uuid4(),
            user_code="EMP001",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            contact_number="1234567890",
            department_id=depts[0].id,
            designation_id=designations[0].id,
            created_by=admin_id
        )
        db.add(emp)
        db.flush()
        print("Added sample employee.")

        # 5. Add Clients
        client = Client(
            id=uuid.uuid4(),
            company_name="Google Cloud",
            industry="Technology",
            created_by=admin_id
        )
        db.add(client)
        db.flush()
        print("Added sample client.")

        # 6. Add Projects
        project = Project(
            id=uuid.uuid4(),
            name="Cloud Transformation",
            project_type="Enterprise",
            department_id=depts[0].id,
            owner_employee_id=emp.id,
            client_id=client.id,
            budget_allocated=Decimal("500000.00"),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180),
            created_by=admin_id
        )
        db.add(project)
        db.flush()
        print("Added sample project.")

        # 7. Add Vendors & Costs
        vendor = Vendor(id=uuid.uuid4(), name="AWS Hosting", service_type="Infrastructure", created_by=admin_id)
        db.add(vendor)
        db.flush()

        cost = ProjectCost(
            id=uuid.uuid4(),
            project_id=project.id,
            vendor_id=vendor.id,
            amount=Decimal("12000.50"),
            cost_type="Subscription",
            expense_date=date.today(),
            created_by=admin_id
        )
        db.add(cost)
        print("Added vendor and sample project cost.")

        # 8. Add Assignment
        assignment = EmployeeProjectAssignment(
            id=uuid.uuid4(),
            employee_id=emp.id,
            project_id=project.id,
            role="Technical Lead",
            allocation_percent=Decimal("100.00"),
            billing_rate=Decimal("150.00"),
            start_date=date.today(),
            created_by=admin_id
        )
        db.add(assignment)
        print("Added project assignment.")

        # 9. Add Invoice & Revenue
        invoice = Invoice(
            id=uuid.uuid4(),
            client_id=client.id,
            project_id=project.id,
            amount=Decimal("25000.00"),
            due_date=date.today() + timedelta(days=30),
            created_by=admin_id
        )
        db.add(invoice)
        db.flush()

        rev = ProjectRevenue(
            id=uuid.uuid4(),
            project_id=project.id,
            client_id=client.id,
            invoice_id=invoice.id,
            revenue_amount=Decimal("25000.00"),
            recognized_date=date.today(),
            created_by=admin_id
        )
        db.add(rev)
        print("Added sample invoice and revenue recognition.")

        db.commit()
        print("--- Database Seeding Completed Successfully ---")

    except Exception as e:
        db.rollback()
        print(f"--- Seeding Failed: {e} ---")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
