"""
User Role model
"""
from sqlalchemy import Column, String, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    permissions = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserRole(id={self.id}, name='{self.name}')>"








