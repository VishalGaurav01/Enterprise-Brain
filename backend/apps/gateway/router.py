from fastapi import APIRouter, Depends
from apps.authService.api.auth import router as auth_router
from apps.employeeService.api.employee import router as employee_router
from apps.employeeService.api.department import router as department_router
from apps.employeeService.api.designation import router as designation_router
from apps.employeeService.api.software_tool import router as software_tool_router
from apps.projectService.api.project import router as project_router
from apps.projectService.api.assignment import router as assignment_router
from apps.projectService.api.vendor import router as vendor_router
from apps.projectService.api.cost import router as cost_router
from apps.financeService.api.client import router as client_router
from apps.financeService.api.invoice import router as invoice_router
from apps.financeService.api.revenue import router as revenue_router
from apps.financeService.api.reimbursement import router as reimbursement_router
from apps.analyticsService.api.rule_engine import router as analytics_router
from apps.shared.security import verify_token
from apps.copilotService.api.copilot import router as copilot_router

# Central Gateway Router with versioning
gateway_router = APIRouter(prefix="/api/v1")

# 1. AUTH (Public endpoints like /login and /register)
gateway_router.include_router(auth_router)

# 2. CORE SERVICES (Protected by Token)
protected_dependencies = [Depends(verify_token)]

gateway_router.include_router(employee_router, dependencies=protected_dependencies)
gateway_router.include_router(department_router, dependencies=protected_dependencies)
gateway_router.include_router(designation_router, dependencies=protected_dependencies)
gateway_router.include_router(software_tool_router, dependencies=protected_dependencies)
gateway_router.include_router(project_router, dependencies=protected_dependencies)
gateway_router.include_router(assignment_router, dependencies=protected_dependencies)
gateway_router.include_router(vendor_router, dependencies=protected_dependencies)
gateway_router.include_router(cost_router, dependencies=protected_dependencies)
gateway_router.include_router(client_router, dependencies=protected_dependencies)
gateway_router.include_router(invoice_router, dependencies=protected_dependencies)
gateway_router.include_router(revenue_router, dependencies=protected_dependencies)
gateway_router.include_router(reimbursement_router, dependencies=protected_dependencies)

# 3. ANALYTICS / INTELLIGENCE
gateway_router.include_router(analytics_router, prefix="/analytics", tags=["Intelligence"])
gateway_router.include_router(copilot_router, prefix="/copilot", tags=["Intelligence"])
