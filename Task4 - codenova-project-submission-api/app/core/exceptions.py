from typing import Any, List, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception returning structured error payload."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[List[Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.code = code
        self.message = message
        self.details = details or []


class NotFoundException(AppException):
    """Raised when a resource is not found or intentionally concealed."""

    def __init__(self, message: str = "Resource not found", details: Optional[List[Any]] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=message,
            details=details,
        )


class UnauthorizedException(AppException):
    """Raised when authentication credentials are missing or invalid."""

    def __init__(
        self,
        message: str = "Could not validate credentials",
        details: Optional[List[Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ):
        auth_headers = {"WWW-Authenticate": "Bearer"}
        if headers:
            auth_headers.update(headers)
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message=message,
            details=details,
            headers=auth_headers,
        )


class ForbiddenException(AppException):
    """Raised when user lacks permission to perform the requested operation."""

    def __init__(self, message: str = "Permission denied", details: Optional[List[Any]] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            message=message,
            details=details,
        )


class BadRequestException(AppException):
    """Raised for malformed or semantically invalid requests."""

    def __init__(self, message: str = "Bad request", details: Optional[List[Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="BAD_REQUEST",
            message=message,
            details=details,
        )


class ValidationException(AppException):
    """Raised when business validation rules fail."""

    def __init__(self, message: str = "The submitted data is invalid", details: Optional[List[Any]] = None):
        super().__init__(
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
            code="VALIDATION_ERROR",
            message=message,
            details=details,
        )
