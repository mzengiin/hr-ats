"""
Security utilities for authentication
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """Token data model"""
    sub: Optional[str] = None
    exp: Optional[datetime] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to verify against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: The encoded JWT refresh token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token
    
    Args:
        token: The JWT token to verify
        
    Returns:
        TokenData: The decoded token data
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise JWTError("Token missing subject")
        
        token_data = TokenData(sub=user_id)
        return token_data
        
    except JWTError as e:
        raise JWTError(f"Token verification failed: {str(e)}")


def verify_refresh_token(token: str) -> TokenData:
    """
    Verify and decode a JWT refresh token
    
    Args:
        token: The JWT refresh token to verify
        
    Returns:
        TokenData: The decoded token data
        
    Raises:
        JWTError: If token is invalid, expired, or not a refresh token
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Check if it's a refresh token
        token_type = payload.get("type")
        if token_type != "refresh":
            raise JWTError("Invalid token type")
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise JWTError("Token missing subject")
        
        token_data = TokenData(sub=user_id)
        return token_data
        
    except JWTError as e:
        raise JWTError(f"Refresh token verification failed: {str(e)}")


def create_token_pair(user_id: str) -> dict:
    """
    Create both access and refresh tokens for a user
    
    Args:
        user_id: The user ID to create tokens for
        
    Returns:
        dict: Dictionary containing access_token and refresh_token
    """
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }








