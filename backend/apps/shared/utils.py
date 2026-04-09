import json
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel


def json_serializer(obj):
    """
    Custom JSON serializer for objects not serializable by default json code.
    Handles UUID, datetime, decimal, and Pydantic models.
    """
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, list):
        return [json_serializer(item) for item in obj]
    if isinstance(obj, dict):
        return {key: json_serializer(value) for key, value in obj.items()}

    return obj
