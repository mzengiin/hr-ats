#!/usr/bin/env python3
"""
Script to add interviews and case studies for all candidates
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.models.case_study import CaseStudy
from app.models.user import User

def add_interviews_and_case_studies():
    """Add interviews and case studies for all candidates"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get all active candidates
        candidates = db.query(Candidate).filter(Candidate.is_active == True).all()
        print(f"Found {len(candidates)} active candidates")
        
        # Get admin user for created_by
        admin_user = db.query(User).filter(User.email == "admin@hrats.com").first()
        if not admin_user:
            print("Admin user not found!")
            return
        
        # Interview titles and types
        interview_titles = [
            "Teknik Mülakat",
            "İK Mülakatı", 
            "Yönetici Mülakatı",
            "HR Mülakatı",
            "Teknik Değerlendirme",
            "Kültür Uyumu Mülakatı",
            "Final Mülakatı"
        ]
        
        interview_types = ["in-person", "video", "phone"]
        interview_statuses = ["scheduled", "completed", "cancelled", "rescheduled"]
        
        # Case study titles and statuses
        case_study_titles = [
            "E-ticaret Platformu API Tasarımı",
            "Mobil Uygulama Performans Optimizasyonu",
            "React Frontend Vaka Çalışması",
            "Backend Sistem Tasarımı",
            "Database Optimizasyonu",
            "Microservices Mimarisi",
            "Full Stack Web Uygulaması",
            "DevOps Pipeline Tasarımı"
        ]
        
        case_study_statuses = ["Beklemede", "Değerlendiriliyor", "Başarılı", "Başarısız"]
        
        # Interviewer names
        interviewers = [
            "Ayşe Demir", "Mehmet Kaya", "Elif Can", "Ali Veli", "Zeynep Özkan",
            "Mustafa Yılmaz", "Fatma Şahin", "Ahmet Kocaman", "Selin Aydın", "Burak Öztürk"
        ]
        
        for candidate in candidates:
            print(f"Processing candidate {candidate.id}: {candidate.first_name} {candidate.last_name}")
            
            # Add 1-3 interviews per candidate
            num_interviews = random.randint(1, 3)
            for i in range(num_interviews):
                # Random dates in the past 30 days
                start_date = datetime.now() - timedelta(days=random.randint(1, 30))
                start_time = start_date.replace(hour=random.randint(9, 17), minute=random.choice([0, 30]))
                end_time = start_time + timedelta(hours=random.randint(1, 2))
                
                interview = Interview(
                    title=f"{candidate.first_name} {candidate.last_name} - {random.choice(interview_titles)}",
                    candidate_id=candidate.id,
                    interviewer_id=admin_user.id,
                    interviewer_name=random.choice(interviewers),
                    start_datetime=start_time,
                    end_datetime=end_time,
                    status=random.choice(interview_statuses),
                    meeting_type=random.choice(interview_types),
                    location=random.choice([
                        "Konferans Salonu A",
                        "Toplantı Odası B", 
                        "Video Konferans",
                        "Telefon Görüşmesi",
                        "Ofis 3. Kat"
                    ]) if random.choice(interview_types) == "in-person" else None,
                    notes=random.choice([
                        "Adayın teknik bilgisi pozisyon için oldukça yeterli. Algoritma sorularına verdiği cevaplar tatmin ediciydi.",
                        "İletişim becerileri güçlü, motivasyonu yüksek ve şirket kültürüne uyum sağlayabilecek bir profil.",
                        "Teknik yeterlilikleri beklentileri karşılıyor. Takım çalışması konusunda deneyimi var.",
                        "Pozisyon için gerekli temel becerilere sahip. İleri seviye konularda gelişim potansiyeli mevcut.",
                        "Mülakat süreci başarılı geçti. Referans kontrolü yapılacak.",
                        ""
                    ]),
                    is_active=True,
                    created_by=admin_user.id,
                    updated_by=admin_user.id
                )
                db.add(interview)
            
            # Add 1-2 case studies per candidate
            num_case_studies = random.randint(1, 2)
            for i in range(num_case_studies):
                # Random due dates in the past 30 days
                due_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                case_study = CaseStudy(
                    title=random.choice(case_study_titles),
                    description=random.choice([
                        "RESTful prensiplerine uygun, ölçeklenebilir ve iyi dokümante edilmiş bir API tasarımı yapın.",
                        "Mevcut mobil uygulamanın performans sorunlarını tespit edin ve optimizasyon önerileri sunun.",
                        "Modern web teknolojileri kullanarak responsive bir frontend uygulaması geliştirin.",
                        "Mikroservis mimarisine uygun bir backend sistemi tasarlayın ve implementasyon planı hazırlayın.",
                        "Veritabanı sorgularını optimize edin ve performans iyileştirmeleri önerin.",
                        "CI/CD pipeline tasarlayın ve deployment stratejisi belirleyin."
                    ]),
                    candidate_id=candidate.id,
                    due_date=due_date,
                    status=random.choice(case_study_statuses),
                    file_path=random.choice([
                        "uploads/case_studies/solution1.pdf",
                        "uploads/case_studies/solution2.pdf", 
                        "uploads/case_studies/solution3.pdf",
                        None
                    ]),
                    notes=random.choice([
                        "RESTful prensiplerine uygun, ölçeklenebilir ve iyi dokümante edilmiş bir API tasarımı sunulmuş. Beklentileri karşıladı.",
                        "Çözüm yaratıcı ve teknik olarak sağlam. Kod kalitesi yüksek.",
                        "Temel gereksinimleri karşılıyor ancak bazı detaylarda eksiklikler var.",
                        "Çözüm beklentileri karşılamıyor. Tekrar değerlendirilmesi gerekiyor.",
                        "İyi bir başlangıç yapılmış ancak geliştirilmesi gereken alanlar mevcut.",
                        ""
                    ]),
                    is_active=True,
                    created_by=admin_user.id,
                    updated_by=admin_user.id
                )
                db.add(case_study)
        
        # Commit all changes
        db.commit()
        print(f"Successfully added interviews and case studies for {len(candidates)} candidates")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_interviews_and_case_studies()
