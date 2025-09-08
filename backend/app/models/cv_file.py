"""
CV File model
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class CVFile(Base):
    __tablename__ = "cv_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="cv_files")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('file_size > 0', name='chk_file_size_positive'),
        CheckConstraint('file_size <= 10485760', name='chk_file_size_limit'),  # 10MB limit
        CheckConstraint("mime_type IN ('application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')", name='chk_mime_type_valid'),
        CheckConstraint('LENGTH(filename) > 0', name='chk_filename_not_empty'),
        CheckConstraint('LENGTH(original_filename) > 0', name='chk_original_filename_not_empty'),
    )
    
    def __repr__(self):
        return f"<CVFile(id={self.id}, filename='{self.filename}', user_id={self.user_id})>"
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        return round(self.file_size / 1024 / 1024, 2)
    
    @property
    def is_pdf(self):
        """Check if file is PDF"""
        return self.mime_type == 'application/pdf'
    
    @property
    def is_doc(self):
        """Check if file is DOC"""
        return self.mime_type == 'application/msword'
    
    @property
    def is_docx(self):
        """Check if file is DOCX"""
        return self.mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
