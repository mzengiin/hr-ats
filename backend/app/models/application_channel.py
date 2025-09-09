"""
Application Channel lookup model
"""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class ApplicationChannel(Base):
    __tablename__ = "application_channels"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ApplicationChannel(id='{self.id}', name='{self.name}')>"

