"""
User schemas for API validation
"""
from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, EmailStr, validator
import re
import uuid


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str
    role_id: uuid.UUID
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '12345678', 'qwerty123', 'admin123',
            'letmein', 'welcome123', 'password123'
        ]
        
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common, please choose a stronger password')
        
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validate name fields"""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        
        if not re.match(r'^[a-zA-Z\s\-\.]+$', v):
            raise ValueError('Name can only contain letters, spaces, hyphens, and periods')
        
        return v.strip()
    


class UserUpdate(BaseModel):
    """Schema for user updates"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[uuid.UUID] = None
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validate name fields"""
        if v is not None:
            if not v.strip():
                raise ValueError('Name cannot be empty')
            
            if len(v.strip()) < 2:
                raise ValueError('Name must be at least 2 characters long')
            
            if not re.match(r'^[a-zA-Z\s\-\.]+$', v):
                raise ValueError('Name can only contain letters, spaces, hyphens, and periods')
            
            return v.strip()
        return v
    


class UserResponse(UserBase):
    """Schema for user response"""
    id: uuid.UUID
    is_active: bool
    role_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for user list response"""
    users: list[UserResponse]
    total: int
    page: int
    pages: int
    limit: int


class UserRoleResponse(BaseModel):
    """Schema for user role response"""
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    permissions: dict
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserWithRoleResponse(UserResponse):
    """Schema for user response with role details"""
    role: Optional[UserRoleResponse] = None


class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '12345678', 'qwerty123', 'admin123',
            'letmein', 'welcome123', 'password123'
        ]
        
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common, please choose a stronger password')
        
        return v


class UserFilter(BaseModel):
    """Schema for user filtering"""
    role_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class RoleResponse(BaseModel):
    """Schema for role response"""
    id: uuid.UUID
    name: str
    description: str
    permissions: Union[dict, list]  # Support both dict and list formats
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


