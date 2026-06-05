from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from apps.employeeService.model.software_tool import SoftwareTool
from apps.employeeService.schema.software_tool import SoftwareToolCreate, SoftwareToolUpdate
from apps.employeeService.repository import software_tool as repo
from apps.authService.schema.auth import UserGet
from apps.shared.responses import SoftwareToolGet


def create_software_tool(session: Session, data: SoftwareToolCreate, current_user: UserGet) -> SoftwareToolGet:
    tool = SoftwareTool(**data.model_dump())
    tool.created_by = current_user.id
    created = repo.create(session, tool)
    return SoftwareToolGet.model_validate(created)


def get_all_software_tools(session: Session, skip: int = 0, limit: int = 100) -> List[SoftwareToolGet]:
    tools = repo.get_all(session, skip, limit)
    return [SoftwareToolGet.model_validate(t) for t in tools]


def get_software_tool_by_id(session: Session, tool_id: UUID) -> Optional[SoftwareToolGet]:
    tool = repo.get_by_id(session, tool_id)
    return SoftwareToolGet.model_validate(tool) if tool else None


def get_tools_by_department(session: Session, department_id: UUID, skip: int = 0, limit: int = 100) -> List[SoftwareToolGet]:
    tools = repo.get_by_department(session, department_id, skip, limit)
    return [SoftwareToolGet.model_validate(t) for t in tools]


def update_software_tool(session: Session, tool_id: UUID, data: SoftwareToolUpdate) -> Optional[SoftwareToolGet]:
    updated_data = data.model_dump(exclude_unset=True)
    updated = repo.update(session, tool_id, updated_data)
    return SoftwareToolGet.model_validate(updated) if updated else None


def delete_software_tool(session: Session, tool_id: UUID) -> bool:
    return repo.delete(session, tool_id)
