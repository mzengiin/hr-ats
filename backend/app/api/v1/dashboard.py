"""
Dashboard API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.candidate import Candidate
from app.models.interview import Interview
from typing import Dict, Any
import random
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/statistics")
async def get_dashboard_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics
    """
    try:
        # Get current month start and end dates
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Total applications (all candidates)
        total_applications = db.query(Candidate).count()
        
        # Active candidates (not rejected or hired)
        active_candidates = db.query(Candidate).filter(
            and_(
                Candidate.is_active == True,
                Candidate.status.notin_(['Reddedildi', 'İşe Alındı'])
            )
        ).count()
        
        # Interviews this month
        interviews_this_month = db.query(Interview).filter(
            and_(
                Interview.is_active == True,
                Interview.start_datetime >= month_start
            )
        ).count()
        
        # Hired candidates
        hired_candidates = db.query(Candidate).filter(
            and_(
                Candidate.is_active == True,
                Candidate.status == 'İşe Alındı'
            )
        ).count()
        
        statistics = {
            "total_applications": total_applications,
            "active_candidates": active_candidates,
            "interviews_this_month": interviews_this_month,
            "hired_candidates": hired_candidates
        }
        
        return {
            "success": True,
            "data": statistics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/candidate-status-distribution")
async def get_candidate_status_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get candidate status distribution
    """
    try:
        # Get status counts from database
        status_counts = db.query(
            Candidate.status,
            func.count(Candidate.id).label('count')
        ).filter(
            Candidate.is_active == True
        ).group_by(Candidate.status).all()
        
        # Calculate total for percentage calculation
        total_candidates = sum(count for _, count in status_counts)
        
        # Define colors for each status
        status_colors = {
            "Başvurdu": "#137fec",
            "İnceleme": "#4ade80", 
            "Mülakat": "#facc15",
            "Teklif": "#f87171",
            "İşe Alındı": "#fb923c",
            "Reddedildi": "#a78bfa",
            "Aktif": "#8b5cf6"
        }
        
        # Build distribution data
        distribution = []
        for status, count in status_counts:
            percentage = (count / total_candidates * 100) if total_candidates > 0 else 0
            distribution.append({
                "status": status,
                "count": count,
                "percentage": round(percentage, 1),
                "color": status_colors.get(status, "#6b7280")
            })
        
        # Sort by count descending
        distribution.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            "success": True,
            "data": distribution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/position-application-volume")
async def get_position_application_volume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get application volume by position
    """
    try:
        # Get position counts from database
        position_counts = db.query(
            Candidate.position,
            func.count(Candidate.id).label('count')
        ).filter(
            Candidate.is_active == True
        ).group_by(Candidate.position).all()
        
        # Calculate total for percentage calculation
        total_applications = sum(count for _, count in position_counts)
        
        # Build position data
        positions = []
        for position, count in position_counts:
            percentage = (count / total_applications * 100) if total_applications > 0 else 0
            positions.append({
                "position": position,
                "count": count,
                "percentage": round(percentage, 1)
            })
        
        # Sort by count descending
        positions.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            "success": True,
            "data": positions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upcoming-interviews")
async def get_upcoming_interviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get upcoming interviews
    """
    try:
        # Get upcoming interviews (next 30 days)
        now = datetime.now()
        future_date = now + timedelta(days=30)
        
        interviews_query = db.query(Interview).join(Candidate).filter(
            and_(
                Interview.is_active == True,
                Interview.start_datetime >= now,
                Interview.start_datetime <= future_date,
                Interview.status.in_(['scheduled', 'confirmed'])
            )
        ).order_by(Interview.start_datetime.asc()).limit(10)
        
        interviews = []
        for interview in interviews_query:
            # Format date and time
            date_str = interview.start_datetime.strftime("%Y-%m-%d")
            time_str = interview.start_datetime.strftime("%H:%M")
            
            # Map status to Turkish
            status_map = {
                'scheduled': 'Planlandı',
                'confirmed': 'Onaylandı',
                'completed': 'Tamamlandı',
                'cancelled': 'İptal',
                'rescheduled': 'Ertelendi'
            }
            
            interviews.append({
                "id": interview.id,
                "candidate_name": interview.candidate.full_name,
                "position": interview.candidate.position,
                "date": date_str,
                "time": time_str,
                "status": status_map.get(interview.status, interview.status),
                "interviewer": interview.interviewer_name
            })
        
        return {
            "success": True,
            "data": interviews
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard-data")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all dashboard data in one request
    """
    try:
        # Get current month start and end dates
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        future_date = now + timedelta(days=30)
        
        # Statistics
        total_applications = db.query(Candidate).count()
        active_candidates = db.query(Candidate).filter(
            and_(
                Candidate.is_active == True,
                Candidate.status.notin_(['Reddedildi', 'İşe Alındı'])
            )
        ).count()
        interviews_this_month = db.query(Interview).filter(
            and_(
                Interview.is_active == True,
                Interview.start_datetime >= month_start
            )
        ).count()
        hired_candidates = db.query(Candidate).filter(
            and_(
                Candidate.is_active == True,
                Candidate.status == 'İşe Alındı'
            )
        ).count()
        
        # Candidate status distribution
        status_counts = db.query(
            Candidate.status,
            func.count(Candidate.id).label('count')
        ).filter(
            Candidate.is_active == True
        ).group_by(Candidate.status).all()
        
        total_candidates = sum(count for _, count in status_counts)
        status_colors = {
            "Başvurdu": "#137fec",
            "İnceleme": "#4ade80", 
            "Mülakat": "#facc15",
            "Teklif": "#f87171",
            "İşe Alındı": "#fb923c",
            "Reddedildi": "#a78bfa",
            "Aktif": "#8b5cf6"
        }
        
        candidate_status_distribution = []
        for status, count in status_counts:
            percentage = (count / total_candidates * 100) if total_candidates > 0 else 0
            candidate_status_distribution.append({
                "status": status,
                "count": count,
                "percentage": round(percentage, 1),
                "color": status_colors.get(status, "#6b7280")
            })
        candidate_status_distribution.sort(key=lambda x: x['count'], reverse=True)
        
        # Position application volume
        position_counts = db.query(
            Candidate.position,
            func.count(Candidate.id).label('count')
        ).filter(
            Candidate.is_active == True
        ).group_by(Candidate.position).all()
        
        total_applications_for_positions = sum(count for _, count in position_counts)
        position_application_volume = []
        for position, count in position_counts:
            percentage = (count / total_applications_for_positions * 100) if total_applications_for_positions > 0 else 0
            position_application_volume.append({
                "position": position,
                "count": count,
                "percentage": round(percentage, 1)
            })
        position_application_volume.sort(key=lambda x: x['count'], reverse=True)
        
        # Upcoming interviews
        interviews_query = db.query(Interview).join(Candidate).filter(
            and_(
                Interview.is_active == True,
                Interview.start_datetime >= now,
                Interview.start_datetime <= future_date,
                Interview.status.in_(['scheduled', 'confirmed'])
            )
        ).order_by(Interview.start_datetime.asc()).limit(10)
        
        upcoming_interviews = []
        for interview in interviews_query:
            date_str = interview.start_datetime.strftime("%Y-%m-%d")
            time_str = interview.start_datetime.strftime("%H:%M")
            
            status_map = {
                'scheduled': 'Planlandı',
                'confirmed': 'Onaylandı',
                'completed': 'Tamamlandı',
                'cancelled': 'İptal',
                'rescheduled': 'Ertelendi'
            }
            
            upcoming_interviews.append({
                "id": interview.id,
                "candidate_name": interview.candidate.full_name,
                "position": interview.candidate.position,
                "date": date_str,
                "time": time_str,
                "status": status_map.get(interview.status, interview.status),
                "interviewer": interview.interviewer_name
            })
        
        dashboard_data = {
            "statistics": {
                "total_applications": total_applications,
                "active_candidates": active_candidates,
                "interviews_this_month": interviews_this_month,
                "hired_candidates": hired_candidates
            },
            "candidate_status_distribution": candidate_status_distribution,
            "position_application_volume": position_application_volume,
            "upcoming_interviews": upcoming_interviews
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

