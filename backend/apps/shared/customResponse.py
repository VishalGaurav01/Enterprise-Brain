from apps.shared.utils import json_serializer


def custom_response(data: dict, message: str, status_code: int, error: str = None):
    """
    Standardize the API response format.
    """
    return {
        "message": message,
        "data": json_serializer(data),
        "error": error,
        "status_code": status_code,
    }
