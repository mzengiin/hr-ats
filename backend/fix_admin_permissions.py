#!/usr/bin/env python3
"""
Fix admin role permissions format
"""
import sys
import os
sys.path.append('/app')

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user_role import UserRole

def fix_admin_permissions():
    """Fix admin role permissions format"""
    db = next(get_db())
    
    try:
        # Find admin role
        admin_role = db.query(UserRole).filter(UserRole.name == "admin").first()
        
        if admin_role:
            # Update permissions to correct format
            admin_role.permissions = {
                "users": ["create", "read", "update", "delete"],
                "roles": ["create", "read", "update", "delete"],
                "auth": ["read", "update"]
            }
            db.commit()
            print("Admin role permissions updated successfully!")
        else:
            print("Admin role not found")
            
    except Exception as e:
        print(f"Error fixing admin permissions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_permissions()
