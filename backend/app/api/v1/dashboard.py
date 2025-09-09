"""
Dashboard API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.user import User
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
        # Mock data - gerçek uygulamada veritabanından gelecek
        statistics = {
            "total_applications": 1250,
            "active_candidates": 320,
            "interviews_this_month": 85,
            "hired_candidates": 15
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
        # Mock data
        distribution = [
            {"status": "Başvurdu", "count": 450, "percentage": 25, "color": "#137fec"},
            {"status": "İnceleme", "count": 360, "percentage": 20, "color": "#4ade80"},
            {"status": "Mülakat", "count": 270, "percentage": 15, "color": "#facc15"},
            {"status": "Teklif", "count": 90, "percentage": 5, "color": "#f87171"},
            {"status": "İşe Alındı", "count": 45, "percentage": 2.5, "color": "#fb923c"},
            {"status": "Reddedildi", "count": 585, "percentage": 32.5, "color": "#a78bfa"}
        ]
        
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
        # Mock data
        positions = [
            {"position": "Yazılım Mühendisi", "count": 200, "percentage": 20},
            {"position": "Ürün Yöneticisi", "count": 700, "percentage": 70},
            {"position": "Pazarlama Uzmanı", "count": 800, "percentage": 80},
            {"position": "Satış Temsilcisi", "count": 1000, "percentage": 100},
            {"position": "Veri Analisti", "count": 900, "percentage": 90},
            {"position": "UX Tasarımcısı", "count": 100, "percentage": 10}
        ]
        
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
        # Mock data
        interviews = [
            {
                "id": 1,
                "candidate_name": "Elif Demir",
                "position": "Yazılım Mühendisi",
                "date": "2024-07-20",
                "time": "10:00",
                "status": "Planlandı",
                "interviewer": "Ayşe Demir"
            },
            {
                "id": 2,
                "candidate_name": "Ahmet Yılmaz",
                "position": "Ürün Yöneticisi",
                "date": "2024-07-21",
                "time": "14:00",
                "status": "Onaylandı",
                "interviewer": "Mehmet Kaya"
            },
            {
                "id": 3,
                "candidate_name": "Ayşe Kaya",
                "position": "Pazarlama Uzmanı",
                "date": "2024-07-22",
                "time": "11:00",
                "status": "Beklemede",
                "interviewer": "Elif Can"
            },
            {
                "id": 4,
                "candidate_name": "Mehmet Can",
                "position": "Satış Temsilcisi",
                "date": "2024-07-23",
                "time": "15:00",
                "status": "Planlandı",
                "interviewer": "Zeynep Öz"
            },
            {
                "id": 5,
                "candidate_name": "Zeynep Tekin",
                "position": "Veri Analisti",
                "date": "2024-07-24",
                "time": "09:00",
                "status": "Onaylandı",
                "interviewer": "Can Yılmaz"
            }
        ]
        
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
        # Mock data - gerçek uygulamada veritabanından gelecek
        dashboard_data = {
            "statistics": {
                "total_applications": 1250,
                "active_candidates": 320,
                "interviews_this_month": 85,
                "hired_candidates": 15
            },
            "candidate_status_distribution": [
                {"status": "Başvurdu", "count": 450, "percentage": 25, "color": "#137fec"},
                {"status": "İnceleme", "count": 360, "percentage": 20, "color": "#4ade80"},
                {"status": "Mülakat", "count": 270, "percentage": 15, "color": "#facc15"},
                {"status": "Teklif", "count": 90, "percentage": 5, "color": "#f87171"},
                {"status": "İşe Alındı", "count": 45, "percentage": 2.5, "color": "#fb923c"},
                {"status": "Reddedildi", "count": 585, "percentage": 32.5, "color": "#a78bfa"}
            ],
            "position_application_volume": [
                {"position": "Yazılım Mühendisi", "count": 200, "percentage": 20},
                {"position": "Ürün Yöneticisi", "count": 700, "percentage": 70},
                {"position": "Pazarlama Uzmanı", "count": 800, "percentage": 80},
                {"position": "Satış Temsilcisi", "count": 1000, "percentage": 100},
                {"position": "Veri Analisti", "count": 900, "percentage": 90},
                {"position": "UX Tasarımcısı", "count": 100, "percentage": 10}
            ],
            "upcoming_interviews": [
                {
                    "id": 1,
                    "candidate_name": "Elif Demir",
                    "position": "Yazılım Mühendisi",
                    "date": "2024-07-20",
                    "time": "10:00",
                    "status": "Planlandı",
                    "interviewer": "Ayşe Demir"
                },
                {
                    "id": 2,
                    "candidate_name": "Ahmet Yılmaz",
                    "position": "Ürün Yöneticisi",
                    "date": "2024-07-21",
                    "time": "14:00",
                    "status": "Onaylandı",
                    "interviewer": "Mehmet Kaya"
                },
                {
                    "id": 3,
                    "candidate_name": "Ayşe Kaya",
                    "position": "Pazarlama Uzmanı",
                    "date": "2024-07-22",
                    "time": "11:00",
                    "status": "Beklemede",
                    "interviewer": "Elif Can"
                },
                {
                    "id": 4,
                    "candidate_name": "Mehmet Can",
                    "position": "Satış Temsilcisi",
                    "date": "2024-07-23",
                    "time": "15:00",
                    "status": "Planlandı",
                    "interviewer": "Zeynep Öz"
                },
                {
                    "id": 5,
                    "candidate_name": "Zeynep Tekin",
                    "position": "Veri Analisti",
                    "date": "2024-07-24",
                    "time": "09:00",
                    "status": "Onaylandı",
                    "interviewer": "Can Yılmaz"
                }
            ]
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

