"""
Case Study API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models import CaseStudy, CaseStudyStatus, Candidate, User
from app.core.auth import get_current_user

router = APIRouter()

# Pydantic schemas
class CaseStudyBase(BaseModel):
    title: str
    description: Optional[str] = None
    candidate_id: int
    due_date: datetime
    status: str = "Beklemede"
    notes: Optional[str] = None

class CaseStudyCreate(CaseStudyBase):
    pass

class CaseStudyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    candidate_id: Optional[int] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class CaseStudyResponse(CaseStudyBase):
    id: int
    candidate_name: str
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CaseStudyListResponse(BaseModel):
    case_studies: List[CaseStudyResponse]
    total: int
    page: int
    per_page: int

class CaseStudyStatusResponse(BaseModel):
    id: str
    name: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=CaseStudyListResponse)
async def get_case_studies(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get case studies with pagination and filtering"""
    
    # Base query
    query = db.query(CaseStudy).filter(CaseStudy.is_active == True)
    
    # Search filter
    if search:
        query = query.join(Candidate).filter(
            or_(
                CaseStudy.title.ilike(f"%{search}%"),
                Candidate.first_name.ilike(f"%{search}%"),
                Candidate.last_name.ilike(f"%{search}%")
            )
        )
    
    # Status filter
    if status:
        query = query.filter(CaseStudy.status == status)
    
    # Sorting
    if sort_by == "title":
        order_field = CaseStudy.title
    elif sort_by == "due_date":
        order_field = CaseStudy.due_date
    elif sort_by == "status":
        order_field = CaseStudy.status
    else:
        order_field = CaseStudy.created_at
    
    if sort_order == "asc":
        query = query.order_by(order_field.asc())
    else:
        query = query.order_by(order_field.desc())
    
    # Get total count
    total = query.count()
    
    # Pagination
    offset = (page - 1) * per_page
    case_studies = query.offset(offset).limit(per_page).all()
    
    # Convert to response format
    case_study_responses = []
    for case_study in case_studies:
        case_study_responses.append(CaseStudyResponse(
            id=case_study.id,
            title=case_study.title,
            description=case_study.description,
            candidate_id=case_study.candidate_id,
            candidate_name=case_study.candidate_name,
            due_date=case_study.due_date,
            status=case_study.status,
            file_path=case_study.file_path,
            notes=case_study.notes,
            created_at=case_study.created_at,
            updated_at=case_study.updated_at
        ))
    
    return CaseStudyListResponse(
        case_studies=case_study_responses,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/{case_study_id}", response_model=CaseStudyResponse)
async def get_case_study(
    case_study_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific case study"""
    case_study = db.query(CaseStudy).filter(
        and_(CaseStudy.id == case_study_id, CaseStudy.is_active == True)
    ).first()
    
    if not case_study:
        raise HTTPException(status_code=404, detail="Case study not found")
    
    return CaseStudyResponse(
        id=case_study.id,
        title=case_study.title,
        description=case_study.description,
        candidate_id=case_study.candidate_id,
        candidate_name=case_study.candidate_name,
        due_date=case_study.due_date,
        status=case_study.status,
        file_path=case_study.file_path,
        notes=case_study.notes,
        created_at=case_study.created_at,
        updated_at=case_study.updated_at
    )

@router.post("/", response_model=CaseStudyResponse)
async def create_case_study(
    case_study: CaseStudyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new case study"""
    
    # Check if candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == case_study.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Create case study
    db_case_study = CaseStudy(
        title=case_study.title,
        description=case_study.description,
        candidate_id=case_study.candidate_id,
        due_date=case_study.due_date,
        status=case_study.status,
        notes=case_study.notes,
        created_by=current_user.id
    )
    
    db.add(db_case_study)
    db.commit()
    db.refresh(db_case_study)
    
    return CaseStudyResponse(
        id=db_case_study.id,
        title=db_case_study.title,
        description=db_case_study.description,
        candidate_id=db_case_study.candidate_id,
        candidate_name=db_case_study.candidate_name,
        due_date=db_case_study.due_date,
        status=db_case_study.status,
        file_path=db_case_study.file_path,
        notes=db_case_study.notes,
        created_at=db_case_study.created_at,
        updated_at=db_case_study.updated_at
    )

@router.put("/{case_study_id}", response_model=CaseStudyResponse)
async def update_case_study(
    case_study_id: int,
    case_study: CaseStudyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a case study"""
    
    db_case_study = db.query(CaseStudy).filter(
        and_(CaseStudy.id == case_study_id, CaseStudy.is_active == True)
    ).first()
    
    if not db_case_study:
        raise HTTPException(status_code=404, detail="Case study not found")
    
    # Update fields
    update_data = case_study.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_case_study, field, value)
    
    db_case_study.updated_by = current_user.id
    db.commit()
    db.refresh(db_case_study)
    
    return CaseStudyResponse(
        id=db_case_study.id,
        title=db_case_study.title,
        description=db_case_study.description,
        candidate_id=db_case_study.candidate_id,
        candidate_name=db_case_study.candidate_name,
        due_date=db_case_study.due_date,
        status=db_case_study.status,
        file_path=db_case_study.file_path,
        notes=db_case_study.notes,
        created_at=db_case_study.created_at,
        updated_at=db_case_study.updated_at
    )

@router.delete("/{case_study_id}")
async def delete_case_study(
    case_study_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a case study (soft delete)"""
    
    db_case_study = db.query(CaseStudy).filter(
        and_(CaseStudy.id == case_study_id, CaseStudy.is_active == True)
    ).first()
    
    if not db_case_study:
        raise HTTPException(status_code=404, detail="Case study not found")
    
    db_case_study.is_active = False
    db_case_study.updated_by = current_user.id
    db.commit()
    
    return {"message": "Case study deleted successfully"}

@router.get("/statuses/", response_model=List[CaseStudyStatusResponse])
async def get_case_study_statuses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all case study statuses"""
    statuses = db.query(CaseStudyStatus).filter(CaseStudyStatus.is_active == True).all()
    return [CaseStudyStatusResponse(id=status.id, name=status.name) for status in statuses]

@router.post("/{case_study_id}/upload")
async def upload_case_study_file(
    case_study_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload file for case study"""
    
    db_case_study = db.query(CaseStudy).filter(
        and_(CaseStudy.id == case_study_id, CaseStudy.is_active == True)
    ).first()
    
    if not db_case_study:
        raise HTTPException(status_code=404, detail="Case study not found")
    
    # Save file (simplified - in production, use proper file storage)
    file_path = f"uploads/case_studies/{case_study_id}_{file.filename}"
    
    # Update case study with file path
    db_case_study.file_path = file_path
    db_case_study.updated_by = current_user.id
    db.commit()
    
    return {"message": "File uploaded successfully", "file_path": file_path}

@router.delete("/{case_study_id}/file")
async def delete_case_study_file(
    case_study_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete file for case study"""
    
    db_case_study = db.query(CaseStudy).filter(
        and_(CaseStudy.id == case_study_id, CaseStudy.is_active == True)
    ).first()
    
    if not db_case_study:
        raise HTTPException(status_code=404, detail="Case study not found")
    
    # Clear file path
    db_case_study.file_path = None
    db_case_study.updated_by = current_user.id
    db.commit()
    
    return {"message": "File deleted successfully"}
