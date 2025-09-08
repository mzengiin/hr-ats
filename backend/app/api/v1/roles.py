"""
Role management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user_role import UserRole
from app.schemas.user import RoleResponse

router = APIRouter()

@router.get("/", response_model=List[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    """Get all available roles"""
    roles = db.query(UserRole).all()
    return roles
