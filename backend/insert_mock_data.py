#!/usr/bin/env python3
"""
Mock data insertion script for HR ATS system
Creates 20 candidates and 20 interviews with diverse data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models import User, Position, ApplicationChannel, CandidateStatus, Candidate, Interview
from faker import Faker
import random
from datetime import datetime, timedelta
import uuid

# Initialize Faker
fake = Faker('tr_TR')  # Turkish locale

# Database connection
DATABASE_URL = "postgresql://cvflow_user:cvflow_password@hr-ats-db-1:5432/cvflow_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clear_existing_data(session):
    """Clear existing candidates and interviews"""
    print("🗑️  Mevcut veriler temizleniyor...")
    
    # Delete interviews first (foreign key constraint)
    session.query(Interview).delete()
    session.query(Candidate).delete()
    
    # Clear lookup tables
    session.query(Position).delete()
    session.query(ApplicationChannel).delete()
    session.query(CandidateStatus).delete()
    
    session.commit()
    print("✅ Veriler temizlendi")

def create_lookup_data(session):
    """Create lookup table data"""
    print("📋 Lookup tabloları oluşturuluyor...")
    
    # Positions
    positions = [
        "Yazılım Geliştirici", "Frontend Developer", "Backend Developer", 
        "Full Stack Developer", "DevOps Engineer", "Data Scientist",
        "UI/UX Designer", "Product Manager", "Project Manager",
        "İnsan Kaynakları Uzmanı", "Muhasebe Uzmanı", "Satış Temsilcisi",
        "Pazarlama Uzmanı", "İçerik Editörü", "Grafik Tasarımcı"
    ]
    
    for i, pos in enumerate(positions):
        position = Position(
            id=f"pos_{i+1}",
            name=pos
        )
        session.add(position)
    
    # Application Channels (must match model constraint)
    channels = [
        "LinkedIn", "Kariyer.net", "Referanslı", "İş Görüşmesi", "Diğer"
    ]
    
    for i, channel in enumerate(channels):
        app_channel = ApplicationChannel(
            id=f"channel_{i+1}",
            name=channel
        )
        session.add(app_channel)
    
    # Candidate Statuses (must match model constraint)
    statuses = [
        "Başvurdu", "İnceleme", "Mülakat", "Teklif", "İşe Alındı", "Reddedildi", "Aktif"
    ]
    
    for i, status in enumerate(statuses):
        candidate_status = CandidateStatus(
            id=f"status_{i+1}",
            name=status
        )
        session.add(candidate_status)
    
    session.commit()
    print("✅ Lookup tabloları oluşturuldu")

def create_candidates(session, count=20):
    """Create mock candidates"""
    print(f"👥 {count} aday oluşturuluyor...")
    
    # Get lookup data
    positions = session.query(Position).all()
    channels = session.query(ApplicationChannel).all()
    statuses = session.query(CandidateStatus).all()
    
    candidates = []
    
    for i in range(count):
        # Generate unique email
        email = f"candidate{i+1}@example.com"
        
        candidate = Candidate(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=email,
            phone=fake.phone_number()[:15],  # Limit phone length
            position=random.choice(positions).name,
            position_id=random.choice(positions).id,
            application_channel=random.choice(channels),
            application_channel_id=random.choice(channels).id,
            status=random.choice(statuses),
            status_id=random.choice(statuses).id,
            application_date=fake.date_time_between(start_date='-6m', end_date='now'),
            hr_specialist=fake.name(),
            notes=fake.text(max_nb_chars=200)
        )
        
        candidates.append(candidate)
        session.add(candidate)
    
    session.commit()
    print(f"✅ {count} aday oluşturuldu")
    return candidates

def create_interviews(session, candidates, count=20):
    """Create mock interviews"""
    print(f"📅 {count} mülakat oluşturuluyor...")
    
    # Get admin user for interviewer
    admin_user = session.query(User).filter(User.email == "admin@hrats.com").first()
    
    interviews = []
    
    for i in range(count):
        # Select random candidate
        candidate = random.choice(candidates)
        
        # Generate interview date (next 30 days)
        interview_date = fake.date_time_between(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        # Generate interview time (9:00-17:00)
        start_datetime = interview_date.replace(
            hour=random.randint(9, 16),
            minute=random.choice([0, 15, 30, 45]),
            second=0,
            microsecond=0
        )
        
        end_datetime = start_datetime + timedelta(hours=random.randint(1, 3))
        
        # Interview types and statuses
        meeting_types = ["in-person", "video", "phone"]
        statuses = ["scheduled", "completed", "cancelled", "rescheduled"]
        
        interview = Interview(
            title=f"{candidate.first_name} {candidate.last_name} - Mülakat",
            candidate_id=candidate.id,
            interviewer_id=admin_user.id if admin_user else None,
            interviewer_name=fake.name(),
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            status=random.choice(statuses),
            meeting_type=random.choice(meeting_types),
            location=fake.address()[:100] if random.choice([True, False]) else f"https://meet.google.com/{fake.word()}-{fake.word()}",
            notes=fake.text(max_nb_chars=300),
            created_at=fake.date_time_between(start_date='-3m', end_date='now'),
            updated_at=datetime.now(),
            created_by=admin_user.id if admin_user else None
        )
        
        interviews.append(interview)
        session.add(interview)
    
    session.commit()
    print(f"✅ {count} mülakat oluşturuldu")
    return interviews

def main():
    """Main function"""
    print("🚀 Mock data oluşturma başlıyor...")
    
    try:
        # Create database session
        session = SessionLocal()
        
        # Clear existing data
        clear_existing_data(session)
        
        # Create lookup data
        create_lookup_data(session)
        
        # Create candidates
        candidates = create_candidates(session, 20)
        
        # Create interviews
        interviews = create_interviews(session, candidates, 20)
        
        # Print summary
        print("\n📊 Özet:")
        print(f"   👥 Aday sayısı: {len(candidates)}")
        print(f"   📅 Mülakat sayısı: {len(interviews)}")
        print(f"   🏢 Pozisyon sayısı: {session.query(Position).count()}")
        print(f"   📱 Başvuru kanalı sayısı: {session.query(ApplicationChannel).count()}")
        print(f"   📊 Aday durumu sayısı: {session.query(CandidateStatus).count()}")
        
        print("\n✅ Mock data başarıyla oluşturuldu!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()