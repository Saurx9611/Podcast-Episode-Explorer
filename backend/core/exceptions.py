from typing import Any, Dict, Optional

class AppException(Exception):
    """Base application exception."""
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "BAD_REQUEST",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} with id '{resource_id}' was not found.",
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "id": resource_id},
        )


class ValidationException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class ConflictException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details,
        )
