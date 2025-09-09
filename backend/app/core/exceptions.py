"""
Custom exceptions for the application
"""
from fastapi import HTTPException, status


class CVFlowException(Exception):
    """Base exception for CVFlow application"""
    pass


class ValidationError(CVFlowException):
    """Validation error"""
    pass


class NotFoundError(CVFlowException):
    """Resource not found error"""
    pass


class AuthenticationError(CVFlowException):
    """Authentication error"""
    pass


class AuthorizationError(CVFlowException):
    """Authorization error"""
    pass


class DuplicateError(CVFlowException):
    """Duplicate resource error"""
    pass


class BusinessLogicError(CVFlowException):
    """Business logic error"""
    pass


def create_http_exception(
    status_code: int,
    detail: str,
    headers: dict = None
) -> HTTPException:
    """
    Create HTTP exception with consistent format
    
    Args:
        status_code: HTTP status code
        detail: Error detail message
        headers: Optional headers
        
    Returns:
        HTTPException: Formatted HTTP exception
    """
    return HTTPException(
        status_code=status_code,
        detail={
            "error": True,
            "message": detail,
            "status_code": status_code
        },
        headers=headers
    )


def validation_error(message: str) -> HTTPException:
    """Create validation error response"""
    return create_http_exception(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"Validation error: {message}"
    )


def not_found_error(resource: str, identifier: str = None) -> HTTPException:
    """Create not found error response"""
    message = f"{resource} not found"
    if identifier:
        message += f" with identifier: {identifier}"
    
    return create_http_exception(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=message
    )


def authentication_error(message: str = "Authentication failed") -> HTTPException:
    """Create authentication error response"""
    return create_http_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"}
    )


def authorization_error(message: str = "Insufficient permissions") -> HTTPException:
    """Create authorization error response"""
    return create_http_exception(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message
    )


def duplicate_error(resource: str, field: str = None) -> HTTPException:
    """Create duplicate error response"""
    message = f"{resource} already exists"
    if field:
        message += f" with {field}"
    
    return create_http_exception(
        status_code=status.HTTP_409_CONFLICT,
        detail=message
    )


def business_logic_error(message: str) -> HTTPException:
    """Create business logic error response"""
    return create_http_exception(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Business logic error: {message}"
    )


def rate_limit_error(retry_after: int = None) -> HTTPException:
    """Create rate limit error response"""
    headers = {}
    if retry_after:
        headers["Retry-After"] = str(retry_after)
    
    return create_http_exception(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Rate limit exceeded",
        headers=headers
    )


def server_error(message: str = "Internal server error") -> HTTPException:
    """Create server error response"""
    return create_http_exception(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=message
    )









