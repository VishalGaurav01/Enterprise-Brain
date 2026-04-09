# Auto-import all project models to ensure SQLAlchemy mapper is fully initialized.
# NOTE: Employee model is imported separately in each entry point (grpc_handler, main.py)
# to avoid circular imports between employeeService and projectService.
from apps.projectService.model.project import Project
from apps.projectService.model.assignment import EmployeeProjectAssignment
from apps.projectService.model.cost import ProjectCost
from apps.projectService.model.vendor import Vendor
