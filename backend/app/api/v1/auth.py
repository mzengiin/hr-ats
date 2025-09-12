"""
Authentication API endpoints
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import uuid

from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest, RefreshTokenRequest, LogoutRequest,
    TokenResponse, RefreshTokenResponse, LogoutResponse,
    UserInfoResponse, PasswordChangeRequest, PasswordChangeResponse,
    ErrorResponse
)
from app.services.auth_service import AuthService
from app.core.auth import get_current_active_user
from app.models.user import User
from app.core.rate_limiter import check_rate_limit, reset_rate_limit

router = APIRouter()


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login user with email and password
    
    Rate limited to prevent brute force attacks
    """
    try:
        # Check rate limit
        check_rate_limit(request)
        
        # Authenticate user
        auth_service = AuthService(db)
        result = auth_service.authenticate_user(login_data.email, login_data.password)
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"],
            user=result["user"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        auth_service = AuthService(db)
        result = auth_service.refresh_access_token(refresh_data.refresh_token)
        
        return RefreshTokenResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
def logout(
    logout_data: LogoutRequest,
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking refresh token
    """
    try:
        auth_service = AuthService(db)
        success = auth_service.logout(logout_data.refresh_token)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logout failed"
            )
        
        return LogoutResponse(message="Logged out successfully")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/me", response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
def get_current_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user information
    
    Requires authentication
    """
    try:
        # Fresh user data from database to avoid cache issues
        fresh_user = db.query(User).filter(User.id == current_user.id).first()
        if not fresh_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user role info
        role_info = None
        if fresh_user.role:
            # Get permissions as list of permission objects with details
            permissions = []
            if hasattr(fresh_user.role, 'permissions') and fresh_user.role.permissions:
                for role_permission in fresh_user.role.permissions:
                    if hasattr(role_permission, 'permission') and role_permission.permission:
                        permission = role_permission.permission
                        permissions.append({
                            "id": str(permission.id),
                            "name": permission.name,
                            "code": permission.code,
                            "description": permission.description,
                            "category": permission.category
                        })
            
            role_info = {
                "id": str(fresh_user.role.id),
                "name": fresh_user.role.name,
                "description": fresh_user.role.description,
                "permissions": permissions
            }
        
        return UserInfoResponse(
            id=str(fresh_user.id),
            email=fresh_user.email,
            first_name=fresh_user.first_name,
            last_name=fresh_user.last_name,
            phone=fresh_user.phone,
            is_active=fresh_user.is_active,
            role=role_info,
            profile_photo=fresh_user.profile_photo,
            created_at=fresh_user.created_at.isoformat(),
            updated_at=fresh_user.updated_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )


@router.post("/change-password", response_model=PasswordChangeResponse, status_code=status.HTTP_200_OK)
def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    Requires authentication
    """
    try:
        auth_service = AuthService(db)
        success = auth_service.change_password(
            current_user.id,
            password_data.current_password,
            password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password change failed"
            )
        
        return PasswordChangeResponse(message="Password changed successfully")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}"
        )


@router.post("/logout-all", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
def logout_all_devices(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Logout from all devices by revoking all user tokens
    
    Requires authentication
    """
    try:
        auth_service = AuthService(db)
        revoked_count = auth_service.revoke_all_user_tokens(current_user.id)
        
        return LogoutResponse(
            message=f"Logged out from all devices. {revoked_count} tokens revoked."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout all failed: {str(e)}"
        )


@router.get("/validate", status_code=status.HTTP_200_OK)
def validate_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate current token
    
    Returns user info if token is valid
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "email": current_user.email
    }


@router.get("/stats", status_code=status.HTTP_200_OK)
def get_auth_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get authentication statistics
    
    Requires authentication
    """
    try:
        auth_service = AuthService(db)
        stats = auth_service.get_auth_stats()
        
        return {
            "message": "Authentication statistics",
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get auth stats: {str(e)}"
        )


@router.post("/cleanup", status_code=status.HTTP_200_OK)
def cleanup_expired_tokens(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cleanup expired tokens
    
    Requires authentication
    """
    try:
        auth_service = AuthService(db)
        cleaned_count = auth_service.cleanup_expired_tokens()
        
        return {
            "message": f"Cleanup completed. {cleaned_count} expired tokens removed."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup failed: {str(e)}"
        )



