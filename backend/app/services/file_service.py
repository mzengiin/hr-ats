"""
File upload and management service
"""
import os
import uuid
import aiofiles
import hashlib
import magic
from typing import List, Optional, Tuple
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.cv_file import CVFile
from app.models.user import User
from app.core.config import settings


class FileService:
    """Service for file upload and management operations"""
    
    # Supported file types and their MIME types
    SUPPORTED_TYPES = {
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
    }
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = "/app/uploads/cv_files"
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """Ensure upload directory exists"""
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """
        Validate uploaded file with security checks
        
        Args:
            file: Uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if file.size and file.size > self.MAX_FILE_SIZE:
            return False, f"File size exceeds {self.MAX_FILE_SIZE // (1024*1024)}MB limit"
        
        # Check if file is empty
        if file.size == 0:
            return False, "Empty file not allowed"
        
        # Read file content for validation
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Check file type by content (more secure than relying on MIME type)
        try:
            detected_mime = magic.from_buffer(content, mime=True)
            if detected_mime not in self.SUPPORTED_TYPES:
                supported_types = list(self.SUPPORTED_TYPES.keys())
                return False, f"Unsupported file type. Detected: {detected_mime}. Supported types: {supported_types}"
        except Exception:
            # If magic detection fails, fall back to declared MIME type
            if file.content_type not in self.SUPPORTED_TYPES:
                supported_types = list(self.SUPPORTED_TYPES.keys())
                return False, f"Unsupported file type. Supported types: {supported_types}"
        
        # Security checks
        security_check, security_error = await self._security_scan(content, file.filename)
        if not security_check:
            return False, security_error
        
        return True, ""
    
    async def _security_scan(self, content: bytes, filename: str) -> Tuple[bool, str]:
        """
        Perform security scan on file content
        
        Args:
            content: File content bytes
            filename: Original filename
            
        Returns:
            Tuple of (is_safe, error_message)
        """
        # Check for suspicious file patterns
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'onload=',
            b'onerror=',
            b'eval(',
            b'exec(',
            b'system(',
            b'cmd.exe',
            b'powershell',
            b'bash',
            b'sh',
        ]
        
        content_lower = content.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                return False, f"File contains suspicious content: {pattern.decode()}"
        
        # Check file extension vs content
        if filename:
            ext = filename.lower().split('.')[-1] if '.' in filename else ''
            if ext == 'exe' or ext == 'bat' or ext == 'cmd' or ext == 'scr':
                return False, "Executable files are not allowed"
        
        # Check for embedded files (basic check)
        if b'PK' in content[:4]:  # ZIP file signature
            return False, "Archive files are not allowed"
        
        return True, ""
    
    async def save_file(self, file: UploadFile, user_id: uuid.UUID) -> CVFile:
        """
        Save uploaded file to disk and database
        
        Args:
            file: Uploaded file object
            user_id: ID of the user uploading the file
            
        Returns:
            CVFile database record
        """
        # Generate unique filename
        file_extension = self.SUPPORTED_TYPES[file.content_type]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file to disk
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Create database record
        cv_file = CVFile(
            user_id=user_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            mime_type=file.content_type
        )
        
        self.db.add(cv_file)
        self.db.commit()
        self.db.refresh(cv_file)
        
        return cv_file
    
    async def upload_files(self, files: List[UploadFile], user_id: uuid.UUID) -> List[CVFile]:
        """
        Upload multiple files
        
        Args:
            files: List of uploaded files
            user_id: ID of the user uploading files
            
        Returns:
            List of CVFile database records
        """
        uploaded_files = []
        
        for file in files:
            # Validate file
            is_valid, error_message = await self.validate_file(file)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_message)
            
            # Save file
            cv_file = await self.save_file(file, user_id)
            uploaded_files.append(cv_file)
        
        return uploaded_files
    
    def get_user_files(self, user_id: uuid.UUID, page: int = 1, limit: int = 20, 
                      sort: str = "upload_date", order: str = "desc") -> dict:
        """
        Get user's files with pagination
        
        Args:
            user_id: ID of the user
            page: Page number
            limit: Items per page
            sort: Sort field
            order: Sort order (asc/desc)
            
        Returns:
            Dictionary with files and pagination info
        """
        query = self.db.query(CVFile).filter(
            CVFile.user_id == user_id,
            CVFile.is_active == True
        )
        
        # Apply sorting
        if sort == "upload_date":
            if order == "desc":
                query = query.order_by(CVFile.upload_date.desc())
            else:
                query = query.order_by(CVFile.upload_date.asc())
        elif sort == "filename":
            if order == "desc":
                query = query.order_by(CVFile.original_filename.desc())
            else:
                query = query.order_by(CVFile.original_filename.asc())
        elif sort == "file_size":
            if order == "desc":
                query = query.order_by(CVFile.file_size.desc())
            else:
                query = query.order_by(CVFile.file_size.asc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        files = query.offset(offset).limit(limit).all()
        
        # Format response
        files_data = []
        for file in files:
            files_data.append({
                "id": str(file.id),
                "filename": file.filename,
                "original_filename": file.original_filename,
                "file_size": file.file_size,
                "mime_type": file.mime_type,
                "upload_date": file.upload_date.isoformat(),
                "download_url": f"/api/v1/files/{file.id}"
            })
        
        return {
            "files": files_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    
    def get_file(self, file_id: uuid.UUID, user_id: uuid.UUID) -> Optional[CVFile]:
        """
        Get file by ID (user must own the file)
        
        Args:
            file_id: ID of the file
            user_id: ID of the user requesting the file
            
        Returns:
            CVFile object or None if not found/not owned by user
        """
        return self.db.query(CVFile).filter(
            CVFile.id == file_id,
            CVFile.user_id == user_id,
            CVFile.is_active == True
        ).first()
    
    def get_file_metadata(self, file_id: uuid.UUID, user_id: uuid.UUID) -> Optional[dict]:
        """
        Get file metadata by ID
        
        Args:
            file_id: ID of the file
            user_id: ID of the user requesting the file
            
        Returns:
            File metadata dictionary or None if not found
        """
        file = self.get_file(file_id, user_id)
        if not file:
            return None
        
        return {
            "id": str(file.id),
            "filename": file.filename,
            "original_filename": file.original_filename,
            "file_size": file.file_size,
            "mime_type": file.mime_type,
            "upload_date": file.upload_date.isoformat(),
            "is_active": file.is_active
        }
    
    def delete_file(self, file_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Soft delete a file
        
        Args:
            file_id: ID of the file to delete
            user_id: ID of the user requesting deletion
            
        Returns:
            True if deleted, False if not found/not owned by user
        """
        file = self.get_file(file_id, user_id)
        if not file:
            return False
        
        # Soft delete
        file.is_active = False
        self.db.commit()
        
        return True
    
    def get_file_path(self, file_id: uuid.UUID, user_id: uuid.UUID) -> Optional[str]:
        """
        Get file path for download
        
        Args:
            file_id: ID of the file
            user_id: ID of the user requesting the file
            
        Returns:
            File path or None if not found/not owned by user
        """
        file = self.get_file(file_id, user_id)
        if not file:
            return None
        
        return file.file_path
