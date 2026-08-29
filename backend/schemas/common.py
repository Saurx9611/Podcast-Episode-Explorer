from typing import Any, Dict, Optional
from pydantic import BaseModel

class ErrorDetails(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: ErrorDetails

class MessageResponse(BaseModel):
    message: str
    success: bool = True
