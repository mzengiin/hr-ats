"""
Simple test to verify models work
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.models.user import User
from app.models.user_role import UserRole
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog
from app.db.base import Base

print("✅ All models imported successfully!")
print("✅ User model:", User.__tablename__)
print("✅ UserRole model:", UserRole.__tablename__)
print("✅ RefreshToken model:", RefreshToken.__tablename__)
print("✅ AuditLog model:", AuditLog.__tablename__)
print("✅ Base metadata tables:", list(Base.metadata.tables.keys()))








