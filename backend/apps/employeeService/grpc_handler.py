import grpc
from concurrent import futures
import logging
from apps.grpcProto.generated import employee_pb2
from apps.grpcProto.generated import employee_pb2_grpc
from apps.employeeService.model.employee import Employee
from apps.employeeService.model.department import Department
from core.config import SessionLocal, DATABASE_URL
from uuid import UUID

# Import all model packages — __init__.py ensures full SQLAlchemy mapper initialization
import apps.employeeService.model
import apps.projectService.model
import apps.financeService.model

class EmployeeGrpcHandler(employee_pb2_grpc.EmployeeServiceServicer):
    def GetEmployee(self, request, context):
        print(f"--- gRPC EmployeeService: Received request for ID: {request.employee_id} ---")
        db = SessionLocal()
        try:
            employee = db.query(Employee).filter(Employee.id == UUID(request.employee_id)).first()
            if not employee:
                print(f"!!! gRPC EmployeeService: Employee {request.employee_id} NOT FOUND in DB !!!")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Employee {request.employee_id} not found")
                return employee_pb2.EmployeeResponse()
            
            return employee_pb2.EmployeeResponse(
                id=str(employee.id),
                user_code=employee.user_code,
                first_name=employee.first_name,
                last_name=employee.last_name,
                email=employee.email,
                department_id=str(employee.department_id) if employee.department_id else "",
                status=employee.status
            )
        except Exception as e:
            print(f"!!! gRPC EmployeeService INTERNAL ERROR: {type(e).__name__}: {e} !!!")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return employee_pb2.EmployeeResponse()
        finally:
            db.close()

def serve():
    print(f"--- gRPC EmployeeService: DB URL is {DATABASE_URL} ---")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    employee_pb2_grpc.add_EmployeeServiceServicer_to_server(EmployeeGrpcHandler(), server)
    server.add_insecure_port('[::]:50051')
    print("Employee gRPC Server started on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
