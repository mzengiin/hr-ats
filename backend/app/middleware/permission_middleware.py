"""
Permission checking middleware
"""
from typing import Callable, List, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class PermissionMiddleware(BaseHTTPMiddleware):
    """Middleware for checking permissions on protected routes"""
    
    def __init__(
        self,
        app,
        protected_routes: Optional[List[str]] = None,
        public_routes: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.protected_routes = protected_routes or []
        self.public_routes = public_routes or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/auth/login",
            "/auth/refresh"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check permissions for protected routes
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response: HTTP response
        """
        # Skip permission check for public routes
        if self._is_public_route(request.url.path):
            return await call_next(request)
        
        # Skip permission check if no protected routes defined
        if not self.protected_routes:
            return await call_next(request)
        
        # Check if route is protected
        if not self._is_protected_route(request.url.path):
            return await call_next(request)
        
        # Get user from request state (set by auth middleware)
        user = getattr(request.state, 'user', None)
        
        if not user:
            logger.warning(f"Unauthorized access attempt to {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Check permissions
        required_permission = self._get_required_permission(request)
        
        if required_permission and not self._has_permission(user, required_permission):
            logger.warning(
                f"Access denied for user {user.email} to {request.url.path}. "
                f"Required permission: {required_permission}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_permission} permission"
            )
        
        return await call_next(request)
    
    def _is_public_route(self, path: str) -> bool:
        """Check if route is public"""
        return any(path.startswith(route) for route in self.public_routes)
    
    def _is_protected_route(self, path: str) -> bool:
        """Check if route is protected"""
        return any(path.startswith(route) for route in self.protected_routes)
    
    def _get_required_permission(self, request: Request) -> Optional[str]:
        """
        Get required permission for the route
        
        Args:
            request: FastAPI request
            
        Returns:
            str: Required permission or None
        """
        # Map routes to permissions
        route_permissions = {
            "/api/v1/users": "users:read",
            "/api/v1/users/": "users:create",
            "/api/v1/candidates": "candidates:read",
            "/api/v1/candidates/": "candidates:create",
            "/api/v1/interviews": "interviews:read",
            "/api/v1/interviews/": "interviews:create",
            "/api/v1/offers": "offers:read",
            "/api/v1/offers/": "offers:create",
        }
        
        # Check for exact match first
        if request.url.path in route_permissions:
            return route_permissions[request.url.path]
        
        # Check for prefix match
        for route, permission in route_permissions.items():
            if request.url.path.startswith(route):
                # Determine permission based on HTTP method
                method_permissions = {
                    "GET": permission.replace(":read", ":read"),
                    "POST": permission.replace(":read", ":create"),
                    "PUT": permission.replace(":read", ":update"),
                    "PATCH": permission.replace(":read", ":update"),
                    "DELETE": permission.replace(":read", ":delete")
                }
                
                return method_permissions.get(request.method, permission)
        
        return None
    
    def _has_permission(self, user, permission: str) -> bool:
        """
        Check if user has required permission
        
        Args:
            user: User object
            permission: Required permission (e.g., "users:create")
            
        Returns:
            bool: True if user has permission
        """
        if not user.role or not user.role.permissions:
            return False
        
        # Parse permission
        resource, action = permission.split(":")
        
        # Check if user has the required permission
        user_permissions = user.role.permissions.get(resource, [])
        
        # If user has admin permission, allow everything
        if "admin" in user.role.permissions:
            return True
        
        return action in user_permissions


class RoleBasedMiddleware(BaseHTTPMiddleware):
    """Middleware for role-based access control"""
    
    def __init__(
        self,
        app,
        role_routes: Optional[dict] = None
    ):
        super().__init__(app)
        self.role_routes = role_routes or {
            "/api/v1/admin": ["admin"],
            "/api/v1/hr": ["admin", "hr"],
            "/api/v1/users": ["admin", "hr"],
            "/api/v1/candidates": ["admin", "hr", "viewer"],
            "/api/v1/interviews": ["admin", "hr", "viewer"],
            "/api/v1/offers": ["admin", "hr", "viewer"]
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check role-based access for routes
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response: HTTP response
        """
        # Get user from request state
        user = getattr(request.state, 'user', None)
        
        if not user:
            return await call_next(request)
        
        # Check if route requires specific roles
        required_roles = self._get_required_roles(request.url.path)
        
        if required_roles and not self._has_required_role(user, required_roles):
            logger.warning(
                f"Access denied for user {user.email} to {request.url.path}. "
                f"Required roles: {required_roles}, User role: {user.role.name if user.role else None}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of the following roles: {', '.join(required_roles)}"
            )
        
        return await call_next(request)
    
    def _get_required_roles(self, path: str) -> Optional[List[str]]:
        """Get required roles for the route"""
        for route, roles in self.role_routes.items():
            if path.startswith(route):
                return roles
        return None
    
    def _has_required_role(self, user, required_roles: List[str]) -> bool:
        """Check if user has one of the required roles"""
        if not user.role:
            return False
        
        return user.role.name in required_roles


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for audit logging"""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log audit information for requests
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response: HTTP response
        """
        # Get user from request state
        user = getattr(request.state, 'user', None)
        
        # Get client information
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} "
            f"user: {user.email if user else 'anonymous'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(
            f"Response: {response.status_code} for {request.method} {request.url.path} "
            f"from {client_ip}"
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded IP first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        return request.client.host if request.client else "unknown"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to response
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response: HTTP response with security headers
        """
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
        
        # Add CSP header
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        return response


def setup_security_middleware(app, config: dict = None):
    """
    Setup all security middleware
    
    Args:
        app: FastAPI application
        config: Configuration dictionary
    """
    if config is None:
        config = {}
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add audit middleware
    app.add_middleware(AuditMiddleware)
    
    # Add role-based middleware
    app.add_middleware(
        RoleBasedMiddleware,
        role_routes=config.get("role_routes")
    )
    
    # Add permission middleware
    app.add_middleware(
        PermissionMiddleware,
        protected_routes=config.get("protected_routes", ["/api/v1"]),
        public_routes=config.get("public_routes")
    )






