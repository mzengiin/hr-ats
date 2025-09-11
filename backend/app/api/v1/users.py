"""
User management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request, Form
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.role import Role
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
import os
import shutil
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    password: str
    role_id: UUID
    is_active: bool = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    role_id: Optional[UUID]
    is_active: bool
    last_login: Optional[str]
    profile_photo: Optional[str]
    role: Optional[dict]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=dict)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all users with pagination and search
    """
    try:
        # Build query
        query = db.query(User)
        
        # Apply search filter
        if search:
            query = query.filter(
                or_(
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.phone.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        users = query.offset(offset).limit(limit).all()
        
        # Format response
        user_list = []
        for user in users:
            user_data = {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "role_id": user.role_id,
                "is_active": user.is_active,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "profile_photo": user.profile_photo,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            }
            
            # Add role information
            if user.role:
                user_data["role"] = {
                    "id": user.role.id,
                    "name": user.role.name,
                    "code": user.role.code
                }
            
            user_list.append(user_data)
        
        total_pages = (total + limit - 1) // limit
        
        return {
            "success": True,
            "data": {
                "users": user_list,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "role_id": user.role_id,
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "profile_photo": user.profile_photo,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
        
        # Add role information
        if user.role:
            user_data["role"] = {
                "id": user.role.id,
                "name": user.role.name,
                "code": user.role.code
            }
        
        return {
            "success": True,
            "data": user_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=dict)
async def create_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    role_id: Optional[UUID] = Form(None),
    is_active: bool = Form(True),
    profile_photo: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new user
    """
    try:
        print(f"Received form data: first_name={first_name}, last_name={last_name}, email={email}, password={'***' if password else 'None'}, role_id={role_id}")
        
        # Validate required fields
        if not password:
            raise HTTPException(
                status_code=422, 
                detail="Password is required"
            )
        
        # Check if user with same email already exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="User with this email already exists"
            )
        
        # Validate role exists
        if role_id:
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise HTTPException(status_code=400, detail="Invalid role ID")
        
        # Handle profile photo upload
        profile_photo_url = None
        if profile_photo:
            # Create uploads directory if it doesn't exist
            upload_dir = "uploads/profile_photos"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = profile_photo.filename.split('.')[-1] if '.' in profile_photo.filename else 'jpg'
            filename = f"{email}_{profile_photo.filename}"
            file_path = os.path.join(upload_dir, filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(profile_photo.file, buffer)
            
            profile_photo_url = f"/uploads/profile_photos/{filename}"
        
        # Create user
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_hash=pwd_context.hash(password) if password else None,
            role_id=role_id,
            is_active=is_active,
            profile_photo=profile_photo_url,
            created_by=current_user.id
        )
        
        db.add(user)
        db.commit()
        
        return {
            "success": True,
            "message": "User created successfully",
            "data": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")
        raise e
    except RequestValidationError as e:
        print(f"Validation error: {e.errors()}")
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {str(e)}")
        print(f"User data: first_name={first_name}, last_name={last_name}, email={email}, role_id={role_id}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: UUID,
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    role_id: Optional[UUID] = Form(None),
    is_active: Optional[bool] = Form(None),
    profile_photo: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a user
    """
    try:
        print(f"Updating user {user_id}: first_name={first_name}, last_name={last_name}, email={email}, role_id={role_id}")
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if email is being changed and if new email already exists
        if email and email != user.email:
            existing_user = db.query(User).filter(
                and_(User.email == email, User.id != user_id)
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=400, 
                    detail="User with this email already exists"
                )
        
        # Validate role exists
        if role_id:
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise HTTPException(status_code=400, detail="Invalid role ID")
        
        # Handle profile photo upload
        if profile_photo:
            # Create uploads directory if it doesn't exist
            upload_dir = "uploads/profile_photos"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = profile_photo.filename.split('.')[-1] if '.' in profile_photo.filename else 'jpg'
            filename = f"{user.email}_{profile_photo.filename}"
            file_path = os.path.join(upload_dir, filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(profile_photo.file, buffer)
            
            user.profile_photo = f"/uploads/profile_photos/{filename}"
        
        # Update user fields
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if email is not None:
            user.email = email
        if phone is not None:
            user.phone = phone
        if password is not None:
            user.password_hash = pwd_context.hash(password)
        if role_id is not None:
            user.role_id = role_id
        if is_active is not None:
            user.is_active = is_active
        
        user.updated_by = current_user.id
        
        db.commit()
        
        return {
            "success": True,
            "message": "User updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user is trying to delete themselves
        if user.id == current_user.id:
            raise HTTPException(
                status_code=400, 
                detail="You cannot delete your own account"
            )
        
        # Delete user
        db.delete(user)
        db.commit()
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))