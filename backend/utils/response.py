"""
Standardized API response format utilities.
"""
from datetime import datetime
from typing import Any, Optional
from fastapi import status
from pydantic import BaseModel


class StandardResponse(BaseModel):
    """Standard API response model."""
    success: bool
    status_code: int
    data: Optional[Any] = None
    message: str
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status_code": 200,
                "data": {"id": "123", "name": "Example"},
                "message": "Operation successful",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


def success_response(
    data: Any,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK
) -> dict:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        Standardized response dictionary
    """
    return {
        "success": True,
        "status_code": status_code,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    data: Optional[Any] = None
) -> dict:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        data: Optional error details
        
    Returns:
        Standardized response dictionary
    """
    return {
        "success": False,
        "status_code": status_code,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def created_response(
    data: Any,
    message: str = "Resource created successfully"
) -> dict:
    """
    Create a standardized 201 Created response.
    
    Args:
        data: Created resource data
        message: Success message
        
    Returns:
        Standardized response dictionary
    """
    return success_response(data, message, status.HTTP_201_CREATED)


def no_content_response(
    message: str = "Resource deleted successfully"
) -> dict:
    """
    Create a standardized 204 No Content response.
    
    Args:
        message: Success message
        
    Returns:
        Standardized response dictionary
    """
    return success_response(None, message, status.HTTP_204_NO_CONTENT)


def unauthorized_response(
    message: str = "Unauthorized access"
) -> dict:
    """
    Create a standardized 401 Unauthorized response.
    
    Args:
        message: Error message
        
    Returns:
        Standardized response dictionary
    """
    return error_response(message, status.HTTP_401_UNAUTHORIZED)


def forbidden_response(
    message: str = "Access forbidden"
) -> dict:
    """
    Create a standardized 403 Forbidden response.
    
    Args:
        message: Error message
        
    Returns:
        Standardized response dictionary
    """
    return error_response(message, status.HTTP_403_FORBIDDEN)


def not_found_response(
    message: str = "Resource not found"
) -> dict:
    """
    Create a standardized 404 Not Found response.
    
    Args:
        message: Error message
        
    Returns:
        Standardized response dictionary
    """
    return error_response(message, status.HTTP_404_NOT_FOUND)


def validation_error_response(
    message: str = "Validation error",
    errors: Optional[dict] = None
) -> dict:
    """
    Create a standardized 422 Validation Error response.
    
    Args:
        message: Error message
        errors: Validation error details
        
    Returns:
        Standardized response dictionary
    """
    return error_response(message, status.HTTP_422_UNPROCESSABLE_ENTITY, errors)


def server_error_response(
    message: str = "Internal server error"
) -> dict:
    """
    Create a standardized 500 Internal Server Error response.
    
    Args:
        message: Error message
        
    Returns:
        Standardized response dictionary
    """
    return error_response(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


# Helper function to wrap any response in standard format
def wrap_response(data: Any, success: bool = True, message: Optional[str] = None, status_code: int = 200) -> dict:
    """
    Wrap any data in standardized response format.
    
    Args:
        data: Data to wrap
        success: Whether operation was successful
        message: Optional message
        status_code: HTTP status code
        
    Returns:
        Standardized response dictionary
    """
    if message is None:
        message = "Success" if success else "Error"
    
    return {
        "success": success,
        "status_code": status_code,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

