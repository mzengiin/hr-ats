"""
Custom middleware for the application
"""
import time
import logging
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Log request start
        start_time = time.time()
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"from {client_ip}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log request completion
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"status={response.status_code} "
            f"time={process_time:.3f}s"
        )
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            
            # Return standardized error response
            from fastapi import HTTPException
            from app.core.exceptions import server_error
            
            if isinstance(e, HTTPException):
                return Response(
                    content=f'{{"error": true, "message": "{e.detail}", "status_code": {e.status_code}}}',
                    status_code=e.status_code,
                    media_type="application/json"
                )
            else:
                return Response(
                    content='{"error": true, "message": "Internal server error", "status_code": 500}',
                    status_code=500,
                    media_type="application/json"
                )


# CORS middleware artık main.py'de tanımlanıyor - çakışmayı önlemek için kaldırıldı


def setup_trusted_host_middleware(app):
    """Setup trusted host middleware"""
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )


def setup_custom_middleware(app):
    """Setup custom middleware"""
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)






