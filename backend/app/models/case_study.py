"""
Case Study model
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class CaseStudy(Base):
    __tablename__ = "case_studies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True, default="Beklemede")
    file_path = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Foreign keys for lookup tables
    status_id = Column(String(50), ForeignKey("case_study_statuses.id"), nullable=True)

    # Relationships
    candidate = relationship("Candidate", backref="case_studies")
    status_rel = relationship("CaseStudyStatus", backref="case_studies")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])

    def __repr__(self):
        return f"<CaseStudy(id={self.id}, title='{self.title}', candidate_id={self.candidate_id})>"

    @property
    def candidate_name(self):
        """Return candidate full name"""
        if self.candidate:
            return f"{self.candidate.first_name} {self.candidate.last_name}"
        return "Bilinmeyen Aday"
