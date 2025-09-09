"""
Token service for managing JWT tokens
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import hashlib
import secrets

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_refresh_token
)
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.config import settings


class TokenService:
    """Service for managing JWT tokens and refresh tokens"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tokens(self, user: User) -> Dict[str, Any]:
        """
        Create access and refresh tokens for a user
        
        Args:
            user: The user to create tokens for
            
        Returns:
            dict: Dictionary containing tokens and user info
        """
        # Create JWT tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token_jwt = create_refresh_token(data={"sub": str(user.id)})
        
        # Create refresh token hash for database storage
        refresh_token_hash = self._hash_token(refresh_token_jwt)
        
        # Store refresh token in database
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        self.db.add(db_refresh_token)
        self.db.commit()
        self.db.refresh(db_refresh_token)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_jwt,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.name if user.role else None
            }
        }
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Create new access token using refresh token
        
        Args:
            refresh_token: The refresh token to use
            
        Returns:
            dict: Dictionary containing new access token
            
        Raises:
            ValueError: If refresh token is invalid
        """
        # Verify refresh token
        try:
            token_data = verify_refresh_token(refresh_token)
        except Exception as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")
        
        # Get user from database
        user = self.db.query(User).filter(User.id == token_data.sub).first()
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        # Verify refresh token exists in database
        refresh_token_hash = self._hash_token(refresh_token)
        db_refresh_token = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.token_hash == refresh_token_hash,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not db_refresh_token:
            raise ValueError("Refresh token not found or expired")
        
        # Create new access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """
        Revoke a refresh token
        
        Args:
            refresh_token: The refresh token to revoke
            
        Returns:
            bool: True if token was revoked, False if not found
        """
        refresh_token_hash = self._hash_token(refresh_token)
        
        db_refresh_token = self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == refresh_token_hash,
            RefreshToken.is_revoked == False
        ).first()
        
        if db_refresh_token:
            db_refresh_token.is_revoked = True
            db_refresh_token.revoked_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    def revoke_all_user_tokens(self, user_id: str) -> int:
        """
        Revoke all refresh tokens for a user
        
        Args:
            user_id: The user ID to revoke tokens for
            
        Returns:
            int: Number of tokens revoked
        """
        tokens = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).all()
        
        count = 0
        for token in tokens:
            token.is_revoked = True
            token.revoked_at = datetime.utcnow()
            count += 1
        
        self.db.commit()
        return count
    
    def cleanup_expired_tokens(self) -> int:
        """
        Remove expired refresh tokens from database
        
        Returns:
            int: Number of tokens removed
        """
        expired_tokens = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).all()
        
        count = len(expired_tokens)
        for token in expired_tokens:
            self.db.delete(token)
        
        self.db.commit()
        return count
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """
        Get user from access token
        
        Args:
            token: The access token
            
        Returns:
            User: The user if token is valid, None otherwise
        """
        try:
            token_data = verify_token(token)
            user = self.db.query(User).filter(
                User.id == token_data.sub,
                User.is_active == True
            ).first()
            return user
        except Exception:
            return None
    
    def _hash_token(self, token: str) -> str:
        """
        Hash a token for database storage
        
        Args:
            token: The token to hash
            
        Returns:
            str: The hashed token
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    def validate_refresh_token(self, refresh_token: str) -> bool:
        """
        Validate if refresh token is valid and not expired
        
        Args:
            refresh_token: The refresh token to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Verify JWT structure
            token_data = verify_refresh_token(refresh_token)
            
            # Check database
            refresh_token_hash = self._hash_token(refresh_token)
            db_refresh_token = self.db.query(RefreshToken).filter(
                RefreshToken.user_id == token_data.sub,
                RefreshToken.token_hash == refresh_token_hash,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            ).first()
            
            return db_refresh_token is not None
            
        except Exception:
            return False









