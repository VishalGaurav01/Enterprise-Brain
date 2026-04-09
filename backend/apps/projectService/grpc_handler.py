import grpc
from concurrent import futures
import logging
from apps.grpcProto.generated import project_pb2
from apps.grpcProto.generated import project_pb2_grpc
from apps.projectService.model.project import Project
from core.database import SessionLocal
from uuid import UUID

# Import all model packages — __init__.py ensures full SQLAlchemy mapper initialization
import apps.employeeService.model
import apps.projectService.model
import apps.financeService.model

class ProjectGrpcHandler(project_pb2_grpc.ProjectServiceServicer):
    def GetProject(self, request, context):
        db = SessionLocal()
        try:
            project = db.query(Project).filter(Project.id == UUID(request.project_id)).first()
            if not project:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Project {request.project_id} not found")
                return project_pb2.ProjectResponse()
            
            return project_pb2.ProjectResponse(
                id=str(project.id),
                name=project.name,
                project_type=project.project_type,
                client_id=str(project.client_id) if project.client_id else "",
                budget_allocated=float(project.budget_allocated) if project.budget_allocated else 0.0,
                status=project.status
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return project_pb2.ProjectResponse()
        finally:
            db.close()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    project_pb2_grpc.add_ProjectServiceServicer_to_server(ProjectGrpcHandler(), server)
    server.add_insecure_port('[::]:50052')
    print("Project gRPC Server started on port 50052")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
