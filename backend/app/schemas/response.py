"""Standardized API Response Schemas"""
from pydantic import BaseModel
from typing import Any, Optional

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Any = None
    error: Optional[str] = None
    status_code: int = 200
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation successful",
                "data": {},
                "error": None,
                "status_code": 200
            }
        }

class ErrorResponse(BaseModel):
    """Error response format"""
    success: bool = False
    message: str
    error: str
    status_code: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Operation failed",
                "error": "Detailed error description",
                "status_code": 400
            }
        }

# Response templates
def success_response(data: Any, message: str = "Success", status_code: int = 200) -> dict:
    """Create standardized success response"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "error": None,
        "status_code": status_code
    }

def error_response(error: str, message: str = "Operation failed", status_code: int = 400) -> dict:
    """Create standardized error response"""
    return {
        "success": False,
        "message": message,
        "error": error,
        "status_code": status_code
    }
