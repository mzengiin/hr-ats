"""
Authentication service for business logic
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid

from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, LogoutRequest
from app.core.security import verify_password
from app.services.token_service import TokenService
from app.core.rate_limiter import check_login_attempts, record_login_attempt


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.token_service = TokenService(db)
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dict containing tokens and user info
            
        Raises:
            ValueError: If credentials are invalid or user is inactive
        """
        # Check login attempts (rate limiting)
        check_login_attempts(email)
        
        # Get user from database
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            record_login_attempt(email, success=False)
            raise ValueError("Invalid credentials")
        
        # Check if user is active
        if not user.is_active:
            record_login_attempt(email, success=False)
            raise ValueError("User account is inactive")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            record_login_attempt(email, success=False)
            raise ValueError("Invalid credentials")
        
        # Record successful login
        record_login_attempt(email, success=True)
        
        # Create tokens
        tokens = self.token_service.create_tokens(user)
        
        return tokens
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Dict containing new access token
            
        Raises:
            ValueError: If refresh token is invalid
        """
        try:
            result = self.token_service.refresh_access_token(refresh_token)
            return result
        except Exception as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")
    
    def logout(self, refresh_token: str) -> bool:
        """
        Logout user by revoking refresh token
        
        Args:
            refresh_token: The refresh token to revoke
            
        Returns:
            bool: True if logout successful
            
        Raises:
            ValueError: If refresh token is invalid
        """
        try:
            success = self.token_service.revoke_refresh_token(refresh_token)
            if not success:
                raise ValueError("Invalid refresh token")
            return True
        except Exception as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")
    
    def get_current_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get current user information from access token
        
        Args:
            access_token: The access token
            
        Returns:
            Dict containing user information
            
        Raises:
            ValueError: If token is invalid
        """
        try:
            user = self.token_service.get_user_from_token(access_token)
            if not user:
                raise ValueError("Invalid token")
            
            # Get user role
            role_info = None
            if user.role:
                role_info = {
                    "id": str(user.role.id),
                    "name": user.role.name,
                    "description": user.role.description,
                    "permissions": user.role.permissions
                }
            
            return {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "is_active": user.is_active,
                "role": role_info,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            }
        except Exception as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    def change_password(
        self,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password changed successfully
            
        Raises:
            ValueError: If user not found or current password incorrect
        """
        from app.services.user_service import UserService
        
        user_service = UserService(self.db)
        return user_service.change_password(
            user_id,
            current_password,
            new_password,
            changed_by=user_id
        )
    
    def validate_token(self, token: str) -> bool:
        """
        Validate if token is valid
        
        Args:
            token: The token to validate
            
        Returns:
            bool: True if token is valid
        """
        try:
            user = self.token_service.get_user_from_token(token)
            return user is not None
        except Exception:
            return False
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """
        Get user from token
        
        Args:
            token: The access token
            
        Returns:
            User: The user if token is valid, None otherwise
        """
        return self.token_service.get_user_from_token(token)
    
    def revoke_all_user_tokens(self, user_id: uuid.UUID) -> int:
        """
        Revoke all tokens for a user
        
        Args:
            user_id: User ID
            
        Returns:
            int: Number of tokens revoked
        """
        return self.token_service.revoke_all_user_tokens(user_id)
    
    def cleanup_expired_tokens(self) -> int:
        """
        Cleanup expired tokens
        
        Returns:
            int: Number of tokens cleaned up
        """
        return self.token_service.cleanup_expired_tokens()
    
    def get_auth_stats(self) -> Dict[str, Any]:
        """
        Get authentication statistics
        
        Returns:
            Dict containing auth statistics
        """
        from app.services.user_service import UserService
        
        user_service = UserService(self.db)
        user_stats = user_service.get_user_stats()
        
        # Add auth-specific stats
        expired_tokens = self.token_service.cleanup_expired_tokens()
        
        return {
            **user_stats,
            "expired_tokens_cleaned": expired_tokens
        }








