"""
Candidate model
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=False)
    position = Column(String(100), nullable=False, index=True)
    application_channel = Column(String(50), nullable=False)
    application_date = Column(DateTime(timezone=True), nullable=False, index=True)
    hr_specialist = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    cv_file_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign keys for lookup tables
    position_id = Column(String(50), ForeignKey("positions.id"), nullable=True)
    application_channel_id = Column(String(50), ForeignKey("application_channels.id"), nullable=True)
    status_id = Column(String(50), ForeignKey("candidate_statuses.id"), nullable=True)
    hr_specialist_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    position_rel = relationship("Position", backref="candidates")
    application_channel_rel = relationship("ApplicationChannel", backref="candidates")
    status_rel = relationship("CandidateStatus", backref="candidates")
    hr_specialist_rel = relationship("User", backref="candidates")
    interviews = relationship("Interview", back_populates="candidate")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('LENGTH(first_name) > 0', name='chk_first_name_not_empty'),
        CheckConstraint('LENGTH(last_name) > 0', name='chk_last_name_not_empty'),
        CheckConstraint('LENGTH(email) > 0', name='chk_email_not_empty'),
        CheckConstraint('LENGTH(phone) > 0', name='chk_phone_not_empty'),
        CheckConstraint('LENGTH(position) > 0', name='chk_position_not_empty'),
        CheckConstraint('LENGTH(application_channel) > 0', name='chk_application_channel_not_empty'),
        CheckConstraint('LENGTH(hr_specialist) > 0', name='chk_hr_specialist_not_empty'),
        CheckConstraint('LENGTH(status) > 0', name='chk_status_not_empty'),
        CheckConstraint("status IN ('Başvurdu', 'İnceleme', 'Mülakat', 'Teklif', 'İşe Alındı', 'Reddedildi', 'Aktif')", name='chk_status_valid'),
        CheckConstraint("application_channel IN ('LinkedIn', 'Kariyer.net', 'Referanslı', 'İş Görüşmesi', 'Diğer')", name='chk_application_channel_valid'),
    )
    
    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.first_name} {self.last_name}', email='{self.email}')>"
    
    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def has_cv(self):
        """Check if candidate has CV file"""
        return self.cv_file_path is not None and self.cv_file_path.strip() != ""
