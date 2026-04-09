import grpc
from concurrent import futures
import logging
from sqlalchemy import func
from apps.grpcProto.generated import finance_pb2
from apps.grpcProto.generated import finance_pb2_grpc
from core.database import SessionLocal
from uuid import UUID

# Import all model packages — __init__.py ensures full SQLAlchemy mapper initialization
import apps.employeeService.model
import apps.projectService.model
import apps.financeService.model

class FinanceGrpcHandler(finance_pb2_grpc.FinanceServiceServicer):
    def GetRevenueSummary(self, request, context):
        db = SessionLocal()
        try:
            # Aggregate revenue for a specific project
            result = db.query(
                func.sum(ProjectRevenue.revenue_amount).label("total"),
                func.count(ProjectRevenue.id).label("count")
            ).filter(ProjectRevenue.project_id == UUID(request.project_id)).first()
            
            total_rev = float(result.total) if result and result.total else 0.0
            count = int(result.count) if result and result.count else 0
            
            return finance_pb2.RevenueSummaryResponse(
                project_id=request.project_id,
                total_revenue=total_rev,
                invoice_count=count
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return finance_pb2.RevenueSummaryResponse()
        finally:
            db.close()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    finance_pb2_grpc.add_FinanceServiceServicer_to_server(FinanceGrpcHandler(), server)
    server.add_insecure_port('[::]:50053')
    print("Finance gRPC Server started on port 50053")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
