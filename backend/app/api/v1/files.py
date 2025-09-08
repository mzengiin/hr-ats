"""
File upload and management API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.file_service import FileService
from app.core.auth import get_current_user
from app.models.user import User
import uuid

router = APIRouter()


@router.get("/")
async def get_user_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all files for the current user
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of user's files
    """
    file_service = FileService(db)
    files = file_service.get_user_files(current_user.id)
    return files


@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload one or multiple CV files
    
    Args:
        files: List of files to upload
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Upload result with file information
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 50:  # Limit to 50 files per upload
        raise HTTPException(status_code=400, detail="Too many files. Maximum 50 files allowed.")
    
    file_service = FileService(db)
    
    try:
        uploaded_files = await file_service.upload_files(files, current_user.id)
        
        # Format response
        files_data = []
        total_size = 0
        
        for file in uploaded_files:
            files_data.append({
                "id": str(file.id),
                "filename": file.filename,
                "original_filename": file.original_filename,
                "file_size": file.file_size,
                "mime_type": file.mime_type,
                "upload_date": file.upload_date.isoformat()
            })
            total_size += file.file_size
        
        return {
            "message": "Files uploaded successfully",
            "uploaded_files": files_data,
            "total_files": len(uploaded_files),
            "total_size": total_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/list")
async def list_files(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: str = Query("upload_date", description="Sort field"),
    order: str = Query("desc", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's uploaded files with pagination
    
    Args:
        page: Page number
        limit: Items per page
        sort: Sort field (upload_date, filename, file_size)
        order: Sort order (asc, desc)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of files with pagination info
    """
    # Validate sort field
    valid_sort_fields = ["upload_date", "filename", "file_size"]
    if sort not in valid_sort_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid sort field. Valid fields: {valid_sort_fields}"
        )
    
    # Validate order
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid order. Use 'asc' or 'desc'"
        )
    
    file_service = FileService(db)
    result = file_service.get_user_files(
        current_user.id, page, limit, sort, order
    )
    
    return result


@router.get("/{file_id}")
async def download_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download a specific file
    
    Args:
        file_id: ID of the file to download
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        File content
    """
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    file_service = FileService(db)
    file_path = file_service.get_file_path(file_uuid, current_user.id)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found or access denied")
    
    # Get file metadata for filename
    file_metadata = file_service.get_file_metadata(file_uuid, current_user.id)
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=file_metadata["original_filename"],
        media_type=file_metadata["mime_type"]
    )


@router.get("/{file_id}/metadata")
async def get_file_metadata(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get file metadata without downloading
    
    Args:
        file_id: ID of the file
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        File metadata
    """
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    file_service = FileService(db)
    metadata = file_service.get_file_metadata(file_uuid, current_user.id)
    
    if not metadata:
        raise HTTPException(status_code=404, detail="File not found or access denied")
    
    return metadata


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a file (soft delete)
    
    Args:
        file_id: ID of the file to delete
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Deletion confirmation
    """
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    file_service = FileService(db)
    success = file_service.delete_file(file_uuid, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="File not found or access denied")
    
    return {
        "message": "File deleted successfully",
        "file_id": file_id
    }
