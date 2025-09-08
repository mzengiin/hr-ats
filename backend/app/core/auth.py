"""
Authentication dependencies and utilities
"""
from datetime import datetime
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.security import verify_token
from app.services.token_service import TokenService

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        user_id = token_data.sub
        
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(
        User.id == user_id,
        User.is_active == True
    ).first()
    
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (additional check for active status)
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        User: The active user
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


def get_token_service(db: Session = Depends(get_db)) -> TokenService:
    """
    Get token service instance
    
    Args:
        db: Database session
        
    Returns:
        TokenService: Token service instance
    """
    return TokenService(db)


def require_role(required_role: str):
    """
    Dependency factory for role-based access control
    
    Args:
        required_role: The required role name
        
    Returns:
        function: Dependency function
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not current_user.role or current_user.role.name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role"
            )
        return current_user
    
    return role_checker


def require_permission(permission: str):
    """
    Dependency factory for permission-based access control
    
    Args:
        permission: The required permission (e.g., "users:read")
        
    Returns:
        function: Dependency function
    """
    def permission_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not current_user.role or not current_user.role.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permissions assigned"
            )
        
        # Parse permission (e.g., "users:read" -> resource="users", action="read")
        try:
            resource, action = permission.split(":")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid permission format: {permission}"
            )
        
        # Check if user has the required permission
        user_permissions = current_user.role.permissions.get(resource, [])
        if action not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {permission} permission"
            )
        
        return current_user
    
    return permission_checker


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None
    
    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session
        
    Returns:
        Optional[User]: The user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token_data = verify_token(credentials.credentials)
        user_id = token_data.sub
        
        if user_id is None:
            return None
            
        user = db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()
        
        return user
        
    except Exception:
        return None


