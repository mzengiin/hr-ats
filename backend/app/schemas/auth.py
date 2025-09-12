"""
Authentication schemas for API validation
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password is not empty"""
        if not v or not v.strip():
            raise ValueError('Password cannot be empty')
        return v.strip()


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str
    
    @validator('refresh_token')
    def validate_refresh_token(cls, v):
        """Validate refresh token is not empty"""
        if not v or not v.strip():
            raise ValueError('Refresh token cannot be empty')
        return v.strip()


class LogoutRequest(BaseModel):
    """Schema for logout request"""
    refresh_token: str
    
    @validator('refresh_token')
    def validate_refresh_token(cls, v):
        """Validate refresh token is not empty"""
        if not v or not v.strip():
            raise ValueError('Refresh token cannot be empty')
        return v.strip()


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: dict


class RefreshTokenResponse(BaseModel):
    """Schema for refresh token response"""
    access_token: str
    token_type: str
    expires_in: int


class LogoutResponse(BaseModel):
    """Schema for logout response"""
    message: str


class UserInfoResponse(BaseModel):
    """Schema for user info response"""
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    is_active: bool
    role: dict
    profile_photo: Optional[str] = None
    created_at: str
    updated_at: str


class PasswordChangeRequest(BaseModel):
    """Schema for password change request"""
    current_password: str
    new_password: str
    
    @validator('current_password', 'new_password')
    def validate_passwords(cls, v):
        """Validate passwords are not empty"""
        if not v or not v.strip():
            raise ValueError('Password cannot be empty')
        return v.strip()
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        
        return v


class PasswordChangeResponse(BaseModel):
    """Schema for password change response"""
    message: str


class ErrorResponse(BaseModel):
    """Schema for error response"""
    error: bool
    message: str
    status_code: int
    details: Optional[dict] = None



