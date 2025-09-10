"""
Interview API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.db.session import get_db
from app.models.interview import Interview
from app.models.candidate import Candidate
from app.models.user import User
from app.core.auth import get_current_user

router = APIRouter()

# Pydantic models
class InterviewBase(BaseModel):
    title: str
    candidate_id: int
    interviewer_name: str
    start_datetime: datetime
    end_datetime: datetime
    status: str = "scheduled"
    meeting_type: str = "in-person"
    location: Optional[str] = None
    notes: Optional[str] = None

class InterviewCreate(InterviewBase):
    pass

class InterviewUpdate(BaseModel):
    title: Optional[str] = None
    candidate_id: Optional[int] = None
    interviewer_name: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    status: Optional[str] = None
    meeting_type: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class InterviewResponse(InterviewBase):
    id: int
    candidate: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InterviewListResponse(BaseModel):
    interviews: List[InterviewResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

def interview_to_response(interview: Interview) -> InterviewResponse:
    """Convert Interview model to InterviewResponse"""
    return InterviewResponse(
        id=interview.id,
        title=interview.title,
        candidate_id=interview.candidate_id,
        interviewer_name=interview.interviewer_name,
        start_datetime=interview.start_datetime,
        end_datetime=interview.end_datetime,
        status=interview.status,
        meeting_type=interview.meeting_type,
        location=interview.location,
        notes=interview.notes,
        candidate={
            "id": interview.candidate.id,
            "name": f"{interview.candidate.first_name} {interview.candidate.last_name}",
            "email": interview.candidate.email,
            "position": interview.candidate.position
        },
        is_active=interview.is_active,
        created_at=interview.created_at,
        updated_at=interview.updated_at
    )

@router.get("/", response_model=InterviewListResponse)
async def get_interviews(
    page: int = 1,
    per_page: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get interviews with pagination and filtering"""
    try:
        # Base query
        query = db.query(Interview).filter(Interview.is_active == True)
        
        # Apply filters
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Interview.start_datetime >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Interview.end_datetime <= end_dt)
        
        if status:
            query = query.filter(Interview.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        interviews = query.offset(offset).limit(per_page).all()
        
        # Convert to response format
        interview_responses = [interview_to_response(i) for i in interviews]
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page
        
        return InterviewListResponse(
            interviews=interview_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        print(f"Error getting interviews: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/calendar")
async def get_calendar_interviews(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """Get interviews for calendar view"""
    try:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        interviews = db.query(Interview).filter(
            and_(
                Interview.is_active == True,
                Interview.start_datetime >= start_dt,
                Interview.end_datetime <= end_dt
            )
        ).all()
        
        # Convert to calendar format
        calendar_events = []
        for interview in interviews:
            calendar_events.append({
                "id": interview.id,
                "title": interview.title,
                "start": interview.start_datetime.isoformat(),
                "end": interview.end_datetime.isoformat(),
                "candidate": {
                    "id": interview.candidate.id,
                    "name": f"{interview.candidate.first_name} {interview.candidate.last_name}",
                    "email": interview.candidate.email,
                    "position": interview.candidate.position
                },
                "interviewer": interview.interviewer_name,
                "status": interview.status,
                "meeting_type": interview.meeting_type,
                "location": interview.location,
                "notes": interview.notes
            })
        
        return {"interviews": calendar_events}
        
    except Exception as e:
        print(f"Error getting calendar interviews: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(interview_id: int, db: Session = Depends(get_db)):
    """Get a specific interview by ID"""
    try:
        interview = db.query(Interview).filter(
            and_(Interview.id == interview_id, Interview.is_active == True)
        ).first()
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        return interview_to_response(interview)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting interview {interview_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(interview_data: InterviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new interview"""
    try:
        # Check if candidate exists
        candidate = db.query(Candidate).filter(
            and_(Candidate.id == interview_data.candidate_id, Candidate.is_active == True)
        ).first()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Check for time conflicts
        existing_interview = db.query(Interview).filter(
            and_(
                Interview.is_active == True,
                Interview.start_datetime < interview_data.end_datetime,
                Interview.end_datetime > interview_data.start_datetime
            )
        ).first()
        
        if existing_interview:
            raise HTTPException(
                status_code=400, 
                detail="Time conflict: Another interview is scheduled at this time"
            )
        
        # Create new interview
        new_interview = Interview(
            title=interview_data.title,
            candidate_id=interview_data.candidate_id,
            interviewer_name=interview_data.interviewer_name,
            start_datetime=interview_data.start_datetime,
            end_datetime=interview_data.end_datetime,
            status=interview_data.status,
            meeting_type=interview_data.meeting_type,
            location=interview_data.location,
            notes=interview_data.notes,
            is_active=True,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        
        db.add(new_interview)
        db.commit()
        db.refresh(new_interview)
        
        return interview_to_response(new_interview)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating interview: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: int, 
    interview_data: InterviewUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an interview"""
    try:
        interview = db.query(Interview).filter(
            and_(Interview.id == interview_id, Interview.is_active == True)
        ).first()
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Check if candidate exists when candidate_id is being updated
        if interview_data.candidate_id is not None:
            candidate = db.query(Candidate).filter(
                and_(Candidate.id == interview_data.candidate_id, Candidate.is_active == True)
            ).first()
            
            if not candidate:
                raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Update fields
        for field, value in interview_data.dict(exclude_unset=True).items():
            setattr(interview, field, value)
        
        interview.updated_at = datetime.utcnow()
        interview.updated_by = current_user.id
        
        db.commit()
        db.refresh(interview)
        
        return interview_to_response(interview)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating interview {interview_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{interview_id}")
async def delete_interview(interview_id: int, db: Session = Depends(get_db)):
    """Delete an interview (soft delete)"""
    try:
        interview = db.query(Interview).filter(
            and_(Interview.id == interview_id, Interview.is_active == True)
        ).first()
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Soft delete
        interview.is_active = False
        interview.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Interview deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting interview {interview_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/candidate/{candidate_id}")
async def get_candidate_interviews(candidate_id: int, db: Session = Depends(get_db)):
    """Get all interviews for a specific candidate"""
    try:
        interviews = db.query(Interview).filter(
            and_(
                Interview.candidate_id == candidate_id,
                Interview.is_active == True
            )
        ).order_by(Interview.start_datetime.desc()).all()
        
        return [interview_to_response(i) for i in interviews]
        
    except Exception as e:
        print(f"Error getting candidate interviews: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
