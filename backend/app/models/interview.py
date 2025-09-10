"""
Interview model
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    interviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    interviewer_name = Column(String(255), nullable=False)  # Mülakat yapan kişinin adı
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=False, default="scheduled")  # scheduled, completed, cancelled, rescheduled
    meeting_type = Column(String(50), nullable=False, default="in-person")  # in-person, video, phone
    location = Column(String(500), nullable=True)  # Konum veya video link
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    interviewer = relationship("User", foreign_keys=[interviewer_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<Interview(id={self.id}, title='{self.title}', start={self.start_datetime})>"
