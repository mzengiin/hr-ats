#!/usr/bin/env python3
"""
Create demo user for testing
"""
import sys
import os
sys.path.append('/app')

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog
from app.core.security import get_password_hash
import uuid

def create_demo_user():
    """Create demo user and role"""
    db = next(get_db())
    
    try:
        # Create admin role if not exists
        admin_role = db.query(UserRole).filter(UserRole.name == "admin").first()
        if not admin_role:
            admin_role = UserRole(
                id=uuid.uuid4(),
                name="admin",
                description="Administrator role",
                permissions={
                    "users": ["create", "read", "update", "delete"],
                    "roles": ["create", "read", "update", "delete"],
                    "auth": ["read", "update"]
                }
            )
            db.add(admin_role)
            db.commit()
            print("Admin role created")
        
        # Create demo user if not exists
        demo_user = db.query(User).filter(User.email == "demo@example.com").first()
        if not demo_user:
            demo_user = User(
                id=uuid.uuid4(),
                email="demo@example.com",
                password_hash=get_password_hash("demo123456"),
                first_name="Demo",
                last_name="User",
                is_active=True,
                role_id=admin_role.id
            )
            db.add(demo_user)
            db.commit()
            print("Demo user created successfully!")
            print("Email: demo@example.com")
            print("Password: demo123456")
        else:
            print("Demo user already exists")
            
    except Exception as e:
        print(f"Error creating demo user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_user()

