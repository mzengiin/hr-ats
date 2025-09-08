"""
User management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid

from app.db.session import get_db
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    UserWithRoleResponse, PasswordChange, UserFilter
)
from app.services.user_service import UserService
from app.core.auth import get_current_active_user, require_permission
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=UserListResponse)
def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:read"))
):
    """
    Get list of users with pagination and filtering
    
    Requires 'users:read' permission
    """
    user_service = UserService(db)
    
    # Validate sort fields
    allowed_sort_fields = ["created_at", "updated_at", "first_name", "last_name", "email"]
    if sort_by not in allowed_sort_fields:
        sort_by = "created_at"
    
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"
    
    # Create filter object
    filters = UserFilter(search=search)
    
    # Calculate skip for pagination
    skip = (page - 1) * limit
    
    # Get users with pagination
    result = user_service.list_users(
        skip=skip,
        limit=limit,
        filters=filters
    )
    
    return UserListResponse(
        users=result["users"],
        total=result["total"],
        page=result["page"],
        pages=result["pages"],
        limit=result["limit"]
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:create"))
):
    """
    Create a new user
    
    Requires 'users:create' permission
    """
    try:
        user_service = UserService(db)
        user = user_service.create_user(user_data, created_by=current_user.id)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/list", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    role_id: Optional[uuid.UUID] = Query(None, description="Filter by role ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    created_after: Optional[str] = Query(None, description="Filter by creation date (ISO format)"),
    created_before: Optional[str] = Query(None, description="Filter by creation date (ISO format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:read"))
):
    """
    List users with pagination and filtering
    
    Requires 'users:read' permission
    """
    try:
        from datetime import datetime
        
        # Parse date filters
        created_after_dt = None
        created_before_dt = None
        
        if created_after:
            try:
                created_after_dt = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid created_after date format. Use ISO format."
                )
        
        if created_before:
            try:
                created_before_dt = datetime.fromisoformat(created_before.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid created_before date format. Use ISO format."
                )
        
        # Create filters
        filters = UserFilter(
            role_id=role_id,
            is_active=is_active,
            search=search,
            created_after=created_after_dt,
            created_before=created_before_dt
        )
        
        user_service = UserService(db)
        skip = (page - 1) * limit
        result = user_service.list_users(skip=skip, limit=limit, filters=filters)
        
        return UserListResponse(
            users=result["users"],
            total=result["total"],
            page=result["page"],
            pages=result["pages"],
            limit=result["limit"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing users: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserWithRoleResponse)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:read"))
):
    """
    Get user by ID
    
    Requires 'users:read' permission
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:update"))
):
    """
    Update user
    
    Requires 'users:update' permission
    """
    try:
        user_service = UserService(db)
        user = user_service.update_user(user_id, user_data, updated_by=current_user.id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:update"))
):
    """
    Deactivate user
    
    Requires 'users:update' permission
    """
    try:
        user_service = UserService(db)
        user = user_service.deactivate_user(user_id, deactivated_by=current_user.id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:update"))
):
    """
    Activate user
    
    Requires 'users:update' permission
    """
    try:
        user_service = UserService(db)
        user = user_service.activate_user(user_id, activated_by=current_user.id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{user_id}/change-password", status_code=status.HTTP_200_OK)
def change_password(
    user_id: uuid.UUID,
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:update"))
):
    """
    Change user password
    
    Requires 'users:update' permission
    """
    try:
        user_service = UserService(db)
        success = user_service.change_password(
            user_id,
            password_data.current_password,
            password_data.new_password,
            changed_by=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
        
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/search/{search_term}", response_model=List[UserResponse])
def search_users(
    search_term: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:read"))
):
    """
    Search users by name or email
    
    Requires 'users:read' permission
    """
    user_service = UserService(db)
    users = user_service.search_users(search_term, limit=limit)
    return users


@router.get("/stats/overview")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:read"))
):
    """
    Get user statistics
    
    Requires 'users:read' permission
    """
    user_service = UserService(db)
    stats = user_service.get_user_stats()
    return stats


@router.get("/role/{role_id}", response_model=List[UserResponse])
def get_users_by_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:read"))
):
    """
    Get all users with a specific role
    
    Requires 'users:read' permission
    """
    user_service = UserService(db)
    users = user_service.get_users_by_role(role_id)
    return users


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:delete"))
):
    """
    Delete user (soft delete)
    
    Requires 'users:delete' permission
    """
    try:
        user_service = UserService(db)
        success = user_service.delete_user(user_id, deleted_by=current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


