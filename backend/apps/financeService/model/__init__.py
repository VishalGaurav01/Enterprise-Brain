# Auto-import all finance models to ensure SQLAlchemy mapper is fully initialized
from apps.financeService.model.client import Client
from apps.financeService.model.invoice import Invoice
from apps.financeService.model.revenue import ProjectRevenue
from apps.financeService.model.reimbursement import Reimbursement
