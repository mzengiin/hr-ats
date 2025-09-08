"""
Session management and token security
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import uuid
import hashlib
import secrets

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.config import settings


class SessionManager:
    """Session management for security"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, user: User, device_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create new user session"""
        session_id = str(uuid.uuid4())
        
        # Create refresh token
        refresh_token = self._generate_refresh_token()
        refresh_token_hash = self._hash_token(refresh_token)
        
        # Store session
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            device_info=device_info or {}
        )
        
        self.db.add(db_refresh_token)
        self.db.commit()
        
        return {
            "session_id": session_id,
            "refresh_token": refresh_token,
            "expires_at": db_refresh_token.expires_at
        }
    
    def validate_session(self, refresh_token: str) -> bool:
        """Validate session token"""
        token_hash = self._hash_token(refresh_token)
        
        db_token = self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        return db_token is not None
    
    def revoke_session(self, refresh_token: str) -> bool:
        """Revoke session"""
        token_hash = self._hash_token(refresh_token)
        
        db_token = self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False
        ).first()
        
        if db_token:
            db_token.is_revoked = True
            db_token.revoked_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    def revoke_all_sessions(self, user_id: uuid.UUID) -> int:
        """Revoke all user sessions"""
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
    
    def cleanup_expired_sessions(self) -> int:
        """Cleanup expired sessions"""
        expired_tokens = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).all()
        
        count = len(expired_tokens)
        for token in expired_tokens:
            self.db.delete(token)
        
        self.db.commit()
        return count
    
    def _generate_refresh_token(self) -> str:
        """Generate secure refresh token"""
        return secrets.token_urlsafe(32)
    
    def _hash_token(self, token: str) -> str:
        """Hash token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()








