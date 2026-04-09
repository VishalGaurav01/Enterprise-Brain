from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

# Import Bases
from apps.employeeService.schema.employee import EmployeeBase
from apps.employeeService.schema.department import DepartmentBase
from apps.employeeService.schema.designation import DesignationBase
from apps.projectService.schema.project import ProjectBase
from apps.projectService.schema.assignment import AssignmentBase
from apps.projectService.schema.vendor import VendorBase
from apps.projectService.schema.cost import ProjectCostBase
from apps.projectService.schema.revenue import ProjectRevenueBase
from apps.projectService.schema.client import ClientBase
from apps.projectService.schema.invoice import InvoiceBase

# ==================== MINIMAL Response Models (To prevent recursion) ====================

class EmployeeGetMinimal(EmployeeBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class DepartmentGetMinimal(DepartmentBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class DesignationGetMinimal(DesignationBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class ProjectGetMinimal(ProjectBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class VendorGetMinimal(VendorBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class ClientGetMinimal(ClientBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class InvoiceGetMinimal(InvoiceBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# ==================== FULL Response Models ====================

class EmployeeGet(EmployeeBase):
    id: UUID
    created_at: datetime
    created_by: Optional[UUID] = None
    department: Optional[DepartmentGetMinimal] = None
    designation: Optional[DesignationGetMinimal] = None
    manager: Optional["EmployeeGetMinimal"] = None
    assignments: Optional[List["AssignmentGet"]] = None
    model_config = ConfigDict(from_attributes=True)

class EmployeeList(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[EmployeeGet]
    model_config = ConfigDict(from_attributes=True)

class DepartmentGet(DepartmentBase):
    id: UUID
    created_at: datetime
    employees: Optional[List[EmployeeGetMinimal]] = None
    projects: Optional[List["ProjectGetMinimal"]] = None
    model_config = ConfigDict(from_attributes=True)

class ProjectGet(ProjectBase):
    id: UUID
    created_at: datetime
    department: Optional[DepartmentGetMinimal] = None
    owner: Optional[EmployeeGetMinimal] = None
    assignments: Optional[List["AssignmentGet"]] = None
    costs: Optional[List["ProjectCostGet"]] = None
    revenues: Optional[List["ProjectRevenueGet"]] = None
    client: Optional["ClientGetMinimal"] = None
    model_config = ConfigDict(from_attributes=True)

class AssignmentGet(AssignmentBase):
    id: UUID
    employee: Optional[EmployeeGetMinimal] = None
    project: Optional[ProjectGetMinimal] = None
    model_config = ConfigDict(from_attributes=True)

class DesignationGet(DesignationBase):
    id: UUID
    employees: Optional[List[EmployeeGetMinimal]] = None
    model_config = ConfigDict(from_attributes=True)

class VendorGet(VendorBase):
    id: UUID
    costs: Optional[List["ProjectCostGet"]] = None
    model_config = ConfigDict(from_attributes=True)

class ProjectCostGet(ProjectCostBase):
    id: UUID
    project: Optional[ProjectGetMinimal] = None
    vendor: Optional[VendorGetMinimal] = None
    model_config = ConfigDict(from_attributes=True)

class ClientGet(ClientBase):
    id: UUID
    projects: Optional[List[ProjectGetMinimal]] = None
    invoices: Optional[List["InvoiceGetMinimal"]] = None
    model_config = ConfigDict(from_attributes=True)

class InvoiceGet(InvoiceBase):
    id: UUID
    client: Optional[ClientGetMinimal] = None
    revenues: Optional[List["ProjectRevenueGet"]] = None
    model_config = ConfigDict(from_attributes=True)

class ProjectRevenueGet(ProjectRevenueBase):
    id: UUID
    project: Optional[ProjectGetMinimal] = None
    invoice: Optional[InvoiceGetMinimal] = None
    client: Optional[ClientGetMinimal] = None
    model_config = ConfigDict(from_attributes=True)
