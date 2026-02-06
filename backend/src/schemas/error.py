from pydantic import BaseModel
from typing import Optional, Dict, Any


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation error",
                "message": "The provided data is invalid",
                "details": {
                    "field": "title",
                    "constraint": "minLength"
                }
            }
        }
