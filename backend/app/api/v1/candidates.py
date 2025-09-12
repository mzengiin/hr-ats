from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid
import os

from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.position import Position
from app.models.application_channel import ApplicationChannel
from app.models.candidate_status import CandidateStatus
from app.models.user import User
from app.models.interview import Interview
from app.models.case_study import CaseStudy

router = APIRouter()

# Pydantic models
class CandidateBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    position: str
    application_channel: str
    application_date: str
    hr_specialist: str
    status: str
    notes: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    application_channel: Optional[str] = None
    application_date: Optional[str] = None
    hr_specialist: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class CandidateResponse(CandidateBase):
    id: int
    cv_file_path: Optional[str] = None
    created_at: str
    updated_at: str

class CandidateListResponse(BaseModel):
    candidates: List[CandidateResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class InterviewResponse(BaseModel):
    id: int
    title: str
    interviewer_name: str
    start_datetime: str
    end_datetime: str
    status: str
    meeting_type: str
    location: Optional[str] = None
    notes: Optional[str] = None

class CaseStudyResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    due_date: str
    status: str
    file_path: Optional[str] = None
    notes: Optional[str] = None

# Mock data constants removed - now using database lookup tables

def candidate_to_response(candidate: Candidate) -> CandidateResponse:
    """Convert Candidate model to CandidateResponse"""
    return CandidateResponse(
        id=candidate.id,
        first_name=candidate.first_name,
        last_name=candidate.last_name,
        email=candidate.email,
        phone=candidate.phone,
        position=candidate.position,
        application_channel=candidate.application_channel,
        application_date=candidate.application_date.isoformat(),
        hr_specialist=candidate.hr_specialist,
        status=candidate.status,
        notes=candidate.notes,
        cv_file_path=candidate.cv_file_path,
        created_at=candidate.created_at.isoformat(),
        updated_at=candidate.updated_at.isoformat()
    )

def interview_to_response(interview: Interview) -> InterviewResponse:
    """Convert Interview model to InterviewResponse"""
    return InterviewResponse(
        id=interview.id,
        title=interview.title,
        interviewer_name=interview.interviewer_name,
        start_datetime=interview.start_datetime.isoformat(),
        end_datetime=interview.end_datetime.isoformat(),
        status=interview.status,
        meeting_type=interview.meeting_type,
        location=interview.location,
        notes=interview.notes
    )

def case_study_to_response(case_study: CaseStudy) -> CaseStudyResponse:
    """Convert CaseStudy model to CaseStudyResponse"""
    return CaseStudyResponse(
        id=case_study.id,
        title=case_study.title,
        description=case_study.description,
        due_date=case_study.due_date.isoformat(),
        status=case_study.status,
        file_path=case_study.file_path,
        notes=case_study.notes
    )

@router.get("/", response_model=CandidateListResponse)
async def get_candidates(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    status: Optional[str] = None,
    position: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get candidates with pagination and filtering"""
    try:
        # Base query
        query = db.query(Candidate).filter(Candidate.is_active == True)
        
        # Apply filters
        if search:
            search_filter = or_(
                Candidate.first_name.ilike(f"%{search}%"),
                Candidate.last_name.ilike(f"%{search}%"),
                Candidate.email.ilike(f"%{search}%"),
                Candidate.position.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if status:
            query = query.filter(Candidate.status == status)
        
        if position:
            query = query.filter(Candidate.position == position)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        candidates = query.offset(offset).limit(per_page).all()
        
        # Convert to response format
        candidate_responses = [candidate_to_response(c) for c in candidates]
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page
        
        return CandidateListResponse(
            candidates=candidate_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        print(f"Error getting candidates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search")
async def search_candidates(
    q: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search candidates by name, email, position, or phone"""
    try:
        if not q or len(q.strip()) < 2:
            return {"candidates": [], "total": 0}
        
        search_term = f"%{q.strip()}%"
        
        # Search in multiple fields
        query = db.query(Candidate).filter(
            and_(
                Candidate.is_active == True,
                or_(
                    Candidate.first_name.ilike(search_term),
                    Candidate.last_name.ilike(search_term),
                    Candidate.email.ilike(search_term),
                    Candidate.position.ilike(search_term),
                    Candidate.phone.ilike(search_term)
                )
            )
        ).limit(limit)
        
        candidates = query.all()
        
        # Convert to response format
        candidate_responses = [candidate_to_response(c) for c in candidates]
        
        return {
            "candidates": candidate_responses,
            "total": len(candidate_responses)
        }
        
    except Exception as e:
        print(f"Error searching candidates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/candidates-options")
async def get_candidate_options(db: Session = Depends(get_db)):
    """Get options for candidate form dropdowns from database"""
    try:
        # Get positions
        positions = db.query(Position).filter(Position.is_active == True).all()
        position_options = [{"id": p.id, "name": p.name} for p in positions]
        
        # Get application channels
        channels = db.query(ApplicationChannel).filter(ApplicationChannel.is_active == True).all()
        application_channel_options = [{"id": c.id, "name": c.name} for c in channels]
        
        # Get candidate statuses
        statuses = db.query(CandidateStatus).filter(CandidateStatus.is_active == True).all()
        status_options = [{"id": s.id, "name": s.name} for s in statuses]
        
        # Get HR specialists (active users)
        hr_specialists = db.query(User).filter(User.is_active == True).all()
        hr_specialist_options = [{"id": str(u.id), "name": f"{u.first_name} {u.last_name}"} for u in hr_specialists]
        
        return {
            "status_options": status_options,
            "position_options": position_options,
            "application_channel_options": application_channel_options,
            "hr_specialist_options": hr_specialist_options
        }
        
    except Exception as e:
        print(f"Error getting candidate options: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get a specific candidate by ID"""
    try:
        candidate = db.query(Candidate).filter(
            and_(Candidate.id == candidate_id, Candidate.is_active == True)
        ).first()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        return candidate_to_response(candidate)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting candidate {candidate_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    application_channel: str = Form(...),
    application_date: str = Form(...),
    hr_specialist: str = Form(...),
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    cv_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create a new candidate"""
    try:
        # Check if email already exists
        existing_candidate = db.query(Candidate).filter(Candidate.email == email).first()
        if existing_candidate:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Parse application date
        try:
            app_date = datetime.fromisoformat(application_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
        
        # Handle CV file upload
        cv_file_path = None
        if cv_file:
            # Validate file type
            file_extension = os.path.splitext(cv_file.filename)[1].lower()
            allowed_extensions = ['.pdf', '.doc', '.docx']
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File type not allowed. Only {', '.join(allowed_extensions)} files are accepted."
                )
            
            # Create upload directory
            upload_dir = "/app/uploads/cv"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate filename with upload date prefix
            upload_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{upload_date}_{first_name.lower()}_{last_name.lower()}_cv{file_extension}"
            cv_file_path = f"/uploads/cv/{filename}"
            
            print(f"NEW CANDIDATE - File extension: {file_extension}")
            print(f"NEW CANDIDATE - Filename: {filename}")
            print(f"NEW CANDIDATE - CV path: {cv_file_path}")
            
            # Save file
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as buffer:
                content = await cv_file.read()
                buffer.write(content)
        
        # Get lookup table IDs
        position_obj = db.query(Position).filter(Position.name == position).first()
        application_channel_obj = db.query(ApplicationChannel).filter(ApplicationChannel.name == application_channel).first()
        status_obj = db.query(CandidateStatus).filter(CandidateStatus.name == status).first()
        
        # Parse hr_specialist name to find user
        hr_specialist_parts = hr_specialist.split(' ')
        if len(hr_specialist_parts) >= 2:
            hr_specialist_obj = db.query(User).filter(
                and_(User.first_name == hr_specialist_parts[0], 
                     User.last_name == ' '.join(hr_specialist_parts[1:]))
            ).first()
        else:
            hr_specialist_obj = None
        
        # Create new candidate
        new_candidate = Candidate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            position=position,
            application_channel=application_channel,
            application_date=app_date,
            hr_specialist=hr_specialist,
            status=status,
            notes=notes,
            cv_file_path=cv_file_path,
            is_active=True,
            # Add foreign key IDs
            position_id=position_obj.id if position_obj else None,
            application_channel_id=application_channel_obj.id if application_channel_obj else None,
            status_id=status_obj.id if status_obj else None,
            hr_specialist_id=hr_specialist_obj.id if hr_specialist_obj else None
        )
        
        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)
        
        return candidate_to_response(new_candidate)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating candidate: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    application_channel: Optional[str] = Form(None),
    application_date: Optional[str] = Form(None),
    hr_specialist: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    cv_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Update a candidate"""
    try:
        candidate = db.query(Candidate).filter(
            and_(Candidate.id == candidate_id, Candidate.is_active == True)
        ).first()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Check email uniqueness if email is being updated
        if email and email != candidate.email:
            existing_candidate = db.query(Candidate).filter(Candidate.email == email).first()
            if existing_candidate:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        # Update fields
        if first_name is not None:
            candidate.first_name = first_name
        if last_name is not None:
            candidate.last_name = last_name
        if email is not None:
            candidate.email = email
        if phone is not None:
            candidate.phone = phone
        if position is not None:
            candidate.position = position
        if application_channel is not None:
            candidate.application_channel = application_channel
        if application_date is not None:
            try:
                candidate.application_date = datetime.fromisoformat(application_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format")
        if hr_specialist is not None:
            candidate.hr_specialist = hr_specialist
        if status is not None:
            candidate.status = status
        if notes is not None:
            candidate.notes = notes
        
        # Update foreign key IDs if lookup fields are being updated
        if position is not None:
            position_obj = db.query(Position).filter(Position.name == position).first()
            candidate.position_id = position_obj.id if position_obj else None
        
        if application_channel is not None:
            application_channel_obj = db.query(ApplicationChannel).filter(ApplicationChannel.name == application_channel).first()
            candidate.application_channel_id = application_channel_obj.id if application_channel_obj else None
        
        if status is not None:
            status_obj = db.query(CandidateStatus).filter(CandidateStatus.name == status).first()
            candidate.status_id = status_obj.id if status_obj else None
        
        if hr_specialist is not None:
            # Parse hr_specialist name to find user
            hr_specialist_parts = hr_specialist.split(' ')
            if len(hr_specialist_parts) >= 2:
                hr_specialist_obj = db.query(User).filter(
                    and_(User.first_name == hr_specialist_parts[0], 
                         User.last_name == ' '.join(hr_specialist_parts[1:]))
                ).first()
            else:
                hr_specialist_obj = None
            candidate.hr_specialist_id = hr_specialist_obj.id if hr_specialist_obj else None
        
        # Handle CV file upload
        if cv_file:
            # Validate file type
            file_extension = os.path.splitext(cv_file.filename)[1].lower()
            allowed_extensions = ['.pdf', '.doc', '.docx']
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File type not allowed. Only {', '.join(allowed_extensions)} files are accepted."
                )
            
            # Create upload directory
            upload_dir = "/app/uploads/cv"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate filename with upload date prefix
            upload_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{upload_date}_{candidate.first_name.lower()}_{candidate.last_name.lower()}_cv{file_extension}"
            cv_file_path = f"/uploads/cv/{filename}"
            
            print(f"UPDATE CANDIDATE - File extension: {file_extension}")
            print(f"UPDATE CANDIDATE - Filename: {filename}")
            print(f"UPDATE CANDIDATE - CV path: {cv_file_path}")
            
            # Save file
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as buffer:
                content = await cv_file.read()
                buffer.write(content)
            
            candidate.cv_file_path = cv_file_path
        
        candidate.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(candidate)
        
        return candidate_to_response(candidate)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating candidate {candidate_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete a candidate (soft delete)"""
    try:
        candidate = db.query(Candidate).filter(
            and_(Candidate.id == candidate_id, Candidate.is_active == True)
        ).first()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Soft delete
        candidate.is_active = False
        candidate.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Candidate deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting candidate {candidate_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{candidate_id}/cv/download")
async def download_candidate_cv(candidate_id: int, db: Session = Depends(get_db)):
    """Download candidate CV file"""
    try:
        candidate = db.query(Candidate).filter(
            and_(Candidate.id == candidate_id, Candidate.is_active == True)
        ).first()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        if not candidate.cv_file_path:
            raise HTTPException(status_code=404, detail="CV file not found")
        
        file_path = f"/app{candidate.cv_file_path}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="CV file not found on disk")
        
        # Get file extension and set appropriate MIME type
        original_filename = os.path.basename(file_path)
        file_extension = os.path.splitext(original_filename)[1]
        file_name = f"{candidate.first_name}_{candidate.last_name}_CV{file_extension}"
        
        print(f"Downloading file: {file_name}, Extension: {file_extension}")
        
        media_type_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain'
        }
        
        media_type = media_type_map.get(file_extension.lower(), 'application/octet-stream')
        
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error downloading CV for candidate {candidate_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{candidate_id}/cv/view")
async def view_candidate_cv(candidate_id: int, db: Session = Depends(get_db)):
    """View candidate CV file in browser"""
    try:
        candidate = db.query(Candidate).filter(
            and_(Candidate.id == candidate_id, Candidate.is_active == True)
        ).first()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        if not candidate.cv_file_path:
            raise HTTPException(status_code=404, detail="CV file not found")
        
        file_path = f"/app{candidate.cv_file_path}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="CV file not found on disk")
        
        # Only allow PDF viewing
        if not candidate.cv_file_path.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files can be viewed in browser")
        
        return FileResponse(
            path=file_path,
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error viewing CV for candidate {candidate_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{candidate_id}/interviews", response_model=List[InterviewResponse])
async def get_candidate_interviews(candidate_id: int, db: Session = Depends(get_db)):
    """Get interviews for a specific candidate"""
    try:
        # Check if candidate exists
        candidate = db.query(Candidate).filter(
            and_(Candidate.id == candidate_id, Candidate.is_active == True)
        ).first()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Get interviews for the candidate
        interviews = db.query(Interview).filter(
            and_(Interview.candidate_id == candidate_id, Interview.is_active == True)
        ).order_by(Interview.start_datetime.desc()).all()
        
        return [interview_to_response(interview) for interview in interviews]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting interviews for candidate {candidate_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{candidate_id}/case-studies", response_model=List[CaseStudyResponse])
async def get_candidate_case_studies(candidate_id: int, db: Session = Depends(get_db)):
    """Get case studies for a specific candidate"""
    try:
        # Check if candidate exists
        candidate = db.query(Candidate).filter(
            and_(Candidate.id == candidate_id, Candidate.is_active == True)
        ).first()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Get case studies for the candidate
        case_studies = db.query(CaseStudy).filter(
            and_(CaseStudy.candidate_id == candidate_id, CaseStudy.is_active == True)
        ).order_by(CaseStudy.due_date.desc()).all()
        
        return [case_study_to_response(case_study) for case_study in case_studies]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting case studies for candidate {candidate_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")