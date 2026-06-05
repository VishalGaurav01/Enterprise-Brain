from sqlalchemy.orm import Session, joinedload
from apps.employeeService.model.software_tool import SoftwareTool
from uuid import UUID
from typing import List, Optional


def create(session: Session, tool: SoftwareTool) -> SoftwareTool:
    session.add(tool)
    session.commit()
    session.refresh(tool)
    return tool


def get_by_id(session: Session, tool_id: UUID) -> Optional[SoftwareTool]:
    return session.query(SoftwareTool).options(
        joinedload(SoftwareTool.department)
    ).filter(SoftwareTool.id == tool_id).first()


def get_all(session: Session, skip: int = 0, limit: int = 100) -> List[SoftwareTool]:
    return session.query(SoftwareTool).options(
        joinedload(SoftwareTool.department)
    ).offset(skip).limit(limit).all()


def get_by_department(session: Session, department_id: UUID, skip: int = 0, limit: int = 100) -> List[SoftwareTool]:
    return session.query(SoftwareTool).options(
        joinedload(SoftwareTool.department)
    ).filter(SoftwareTool.department_id == department_id).offset(skip).limit(limit).all()


def update(session: Session, tool_id: UUID, data: dict) -> Optional[SoftwareTool]:
    tool = get_by_id(session, tool_id)
    if not tool:
        return None
    for key, value in data.items():
        if hasattr(tool, key):
            setattr(tool, key, value)
    session.commit()
    session.refresh(tool)
    return tool


def delete(session: Session, tool_id: UUID) -> bool:
    tool = get_by_id(session, tool_id)
    if tool:
        session.delete(tool)
        session.commit()
        return True
    return False
