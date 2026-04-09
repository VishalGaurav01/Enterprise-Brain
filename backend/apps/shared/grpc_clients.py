import grpc
from apps.grpcProto.generated import employee_pb2
from apps.grpcProto.generated import employee_pb2_grpc
from apps.grpcProto.generated import project_pb2
from apps.grpcProto.generated import project_pb2_grpc
from apps.grpcProto.generated import finance_pb2
from apps.grpcProto.generated import finance_pb2_grpc
import os

class GrpcClients:
    # Use environment variables for flexibility in Docker/K8s
    EMPLOYEE_SERVICE_ADDR = os.getenv("EMPLOYEE_SERVICE_GRPC_ADDR", "localhost:50051")
    PROJECT_SERVICE_ADDR = os.getenv("PROJECT_SERVICE_GRPC_ADDR", "localhost:50052")
    FINANCE_SERVICE_ADDR = os.getenv("FINANCE_SERVICE_GRPC_ADDR", "localhost:50053")

    @staticmethod
    def get_employee(employee_id: str):
        with grpc.insecure_channel(GrpcClients.EMPLOYEE_SERVICE_ADDR) as channel:
            stub = employee_pb2_grpc.EmployeeServiceStub(channel)
            try:
                response = stub.GetEmployee(employee_pb2.GetEmployeeRequest(employee_id=employee_id))
                return response
            except grpc.RpcError as e:
                print(f"gRPC Error (GetEmployee): {e.code()} - {e.details()}")
                return None

    @staticmethod
    def get_project(project_id: str):
        with grpc.insecure_channel(GrpcClients.PROJECT_SERVICE_ADDR) as channel:
            stub = project_pb2_grpc.ProjectServiceStub(channel)
            try:
                response = stub.GetProject(project_pb2.GetProjectRequest(project_id=project_id))
                return response
            except grpc.RpcError as e:
                print(f"gRPC Error (GetProject): {e.code()} - {e.details()}")
                return None

    @staticmethod
    def get_revenue_summary(project_id: str):
        with grpc.insecure_channel(GrpcClients.FINANCE_SERVICE_ADDR) as channel:
            stub = finance_pb2_grpc.FinanceServiceStub(channel)
            try:
                response = stub.GetRevenueSummary(finance_pb2.RevenueSummaryRequest(project_id=project_id))
                return response
            except grpc.RpcError as e:
                print(f"gRPC Error (GetRevenueSummary): {e.code()} - {e.details()}")
                return None
