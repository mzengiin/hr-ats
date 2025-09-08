#!/usr/bin/env python3
"""
Test user permissions and fix admin role
"""
import sys
import os
sys.path.append('/app')

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.core.security import get_password_hash
import uuid

def test_and_fix_permissions():
    """Test and fix user permissions"""
    db = next(get_db())
    
    try:
        print("=== Testing User Permissions ===")
        
        # Check if admin role exists
        admin_role = db.query(UserRole).filter(UserRole.name == "admin").first()
        if admin_role:
            print(f"Admin role found: {admin_role.name}")
            print(f"Current permissions: {admin_role.permissions}")
            print(f"Permissions type: {type(admin_role.permissions)}")
            
            # Fix permissions if they're in wrong format
            if isinstance(admin_role.permissions, list):
                print("Fixing admin role permissions...")
                admin_role.permissions = {
                    "users": ["create", "read", "update", "delete"],
                    "roles": ["create", "read", "update", "delete"],
                    "auth": ["read", "update"]
                }
                db.commit()
                print("Admin role permissions fixed!")
            else:
                print("Admin role permissions are already in correct format")
        else:
            print("Admin role not found, creating...")
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
            print("Admin role created!")
        
        # Check if demo user exists
        demo_user = db.query(User).filter(User.email == "demo@example.com").first()
        if demo_user:
            print(f"Demo user found: {demo_user.email}")
            print(f"User role: {demo_user.role.name if demo_user.role else 'None'}")
            print(f"User permissions: {demo_user.role.permissions if demo_user.role else 'None'}")
        else:
            print("Demo user not found, creating...")
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
            print("Demo user created!")
        
        # Test permission checking
        if demo_user and demo_user.role:
            print("\n=== Testing Permission Checks ===")
            
            # Test users:read permission
            user_permissions = demo_user.role.permissions.get("users", [])
            has_read = "read" in user_permissions
            print(f"Has users:read permission: {has_read}")
            
            # Test users:create permission
            has_create = "create" in user_permissions
            print(f"Has users:create permission: {has_create}")
            
            # Test users:update permission
            has_update = "update" in user_permissions
            print(f"Has users:update permission: {has_update}")
            
            # Test users:delete permission
            has_delete = "delete" in user_permissions
            print(f"Has users:delete permission: {has_delete}")
            
        print("\n=== Test Complete ===")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_and_fix_permissions()
