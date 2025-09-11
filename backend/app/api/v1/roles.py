"""
Role management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.role import Role, Permission, RolePermission
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

router = APIRouter()


class RoleCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True
    permissions: List[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permissions: Optional[List[str]] = None


class RoleResponse(BaseModel):
    id: UUID
    name: str
    code: str
    description: Optional[str]
    is_active: bool
    user_count: int
    permissions: List[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=dict)
async def get_roles(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all roles with pagination and search
    """
    try:
        # Build query
        query = db.query(Role)
        
        # Apply search filter
        if search:
            query = query.filter(
                or_(
                    Role.name.ilike(f"%{search}%"),
                    Role.code.ilike(f"%{search}%"),
                    Role.description.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        roles = query.offset(offset).limit(limit).all()
        
        # Format response
        role_list = []
        for role in roles:
            # Get permissions for this role
            permissions = db.query(Permission.code).join(RolePermission).filter(
                RolePermission.role_id == role.id
            ).all()
            
            role_list.append({
                "id": role.id,
                "name": role.name,
                "code": role.code,
                "description": role.description,
                "is_active": role.is_active,
                "user_count": role.user_count,
                "permissions": [p.code for p in permissions],
                "created_at": role.created_at.isoformat(),
                "updated_at": role.updated_at.isoformat()
            })
        
        total_pages = (total + limit - 1) // limit
        
        return {
            "success": True,
            "data": {
                "roles": role_list,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{role_id}", response_model=dict)
async def get_role(
    role_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific role by ID
    """
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Get permissions for this role
        permissions = db.query(Permission.code).join(RolePermission).filter(
            RolePermission.role_id == role.id
        ).all()
        
        return {
            "success": True,
            "data": {
                "id": role.id,
                "name": role.name,
                "code": role.code,
                "description": role.description,
                "is_active": role.is_active,
                "user_count": role.user_count,
                "permissions": [p.code for p in permissions],
                "created_at": role.created_at.isoformat(),
                "updated_at": role.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=dict)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new role
    """
    try:
        # Check if role with same name or code already exists
        existing_role = db.query(Role).filter(
            or_(Role.name == role_data.name, Role.code == role_data.code)
        ).first()
        
        if existing_role:
            raise HTTPException(
                status_code=400, 
                detail="Role with this name or code already exists"
            )
        
        # Create role
        role = Role(
            name=role_data.name,
            code=role_data.code,
            description=role_data.description,
            is_active=role_data.is_active,
            created_by=current_user.id
        )
        
        db.add(role)
        db.flush()  # Get the role ID
        
        # Add permissions
        if role_data.permissions:
            for permission_code in role_data.permissions:
                permission = db.query(Permission).filter(
                    Permission.code == permission_code
                ).first()
                
                if permission:
                    role_permission = RolePermission(
                        role_id=role.id,
                        permission_id=permission.id
                    )
                    db.add(role_permission)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Role created successfully",
            "data": {
                "id": role.id,
                "name": role.name,
                "code": role.code
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{role_id}", response_model=dict)
async def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a role
    """
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Check if role with same name or code already exists (excluding current role)
        if role_data.name or role_data.code:
            existing_role = db.query(Role).filter(
                and_(
                    Role.id != role_id,
                    or_(
                        Role.name == role_data.name if role_data.name else False,
                        Role.code == role_data.code if role_data.code else False
                    )
                )
            ).first()
            
            if existing_role:
                raise HTTPException(
                    status_code=400, 
                    detail="Role with this name or code already exists"
                )
        
        # Update role fields
        if role_data.name is not None:
            role.name = role_data.name
        if role_data.code is not None:
            role.code = role_data.code
        if role_data.description is not None:
            role.description = role_data.description
        if role_data.is_active is not None:
            role.is_active = role_data.is_active
        
        role.updated_by = current_user.id
        
        # Update permissions if provided
        if role_data.permissions is not None:
            # Remove existing permissions
            db.query(RolePermission).filter(
                RolePermission.role_id == role.id
            ).delete()
            
            # Add new permissions
            for permission_code in role_data.permissions:
                permission = db.query(Permission).filter(
                    Permission.code == permission_code
                ).first()
                
                if permission:
                    role_permission = RolePermission(
                        role_id=role.id,
                        permission_id=permission.id
                    )
                    db.add(role_permission)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Role updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{role_id}", response_model=dict)
async def delete_role(
    role_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a role
    """
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Check if role is assigned to any users
        user_count = db.query(User).filter(User.role_id == role_id).count()
        if user_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete role. It is assigned to {user_count} user(s)"
            )
        
        # Delete role permissions
        db.query(RolePermission).filter(
            RolePermission.role_id == role.id
        ).delete()
        
        # Delete role
        db.delete(role)
        db.commit()
        
        return {
            "success": True,
            "message": "Role deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/permissions/list", response_model=dict)
async def get_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all available permissions
    """
    try:
        permissions = db.query(Permission).filter(Permission.is_active == True).all()
        
        permission_list = []
        for permission in permissions:
            permission_list.append({
                "id": permission.id,
                "name": permission.name,
                "code": permission.code,
                "description": permission.description,
                "category": permission.category
            })
        
        return {
            "success": True,
            "data": permission_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))