#!/usr/bin/env python3
"""
Simple mock data insertion script for HR ATS system
Creates 20 candidates and 20 interviews with basic data
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

# Initialize Faker
fake = Faker('tr_TR')

# Database connection
DATABASE_URL = "postgresql://cvflow_user:cvflow_password@hr-ats-db-1:5432/cvflow_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clear_and_create_data():
    """Clear existing data and create new mock data"""
    print("🚀 Mock data oluşturma başlıyor...")
    
    session = SessionLocal()
    
    try:
        # Clear existing data
        print("🗑️  Mevcut veriler temizleniyor...")
        session.execute(text("DELETE FROM interviews"))
        session.execute(text("DELETE FROM candidates"))
        session.execute(text("DELETE FROM positions"))
        session.execute(text("DELETE FROM application_channels"))
        session.execute(text("DELETE FROM candidate_statuses"))
        session.commit()
        print("✅ Veriler temizlendi")
        
        # Create positions
        print("📋 Pozisyonlar oluşturuluyor...")
        positions_data = [
            ("pos_1", "Yazılım Geliştirici"),
            ("pos_2", "Frontend Developer"),
            ("pos_3", "Backend Developer"),
            ("pos_4", "Full Stack Developer"),
            ("pos_5", "DevOps Engineer"),
            ("pos_6", "Data Scientist"),
            ("pos_7", "UI/UX Designer"),
            ("pos_8", "Product Manager"),
            ("pos_9", "Project Manager"),
            ("pos_10", "İnsan Kaynakları Uzmanı")
        ]
        
        for pos_id, pos_name in positions_data:
            session.execute(text(
                "INSERT INTO positions (id, name, is_active, created_at, updated_at) "
                "VALUES (:id, :name, true, NOW(), NOW())"
            ), {"id": pos_id, "name": pos_name})
        
        # Create application channels
        print("📱 Başvuru kanalları oluşturuluyor...")
        channels_data = [
            ("channel_1", "LinkedIn"),
            ("channel_2", "Kariyer.net"),
            ("channel_3", "Referanslı"),
            ("channel_4", "İş Görüşmesi"),
            ("channel_5", "Diğer")
        ]
        
        for ch_id, ch_name in channels_data:
            session.execute(text(
                "INSERT INTO application_channels (id, name, is_active, created_at, updated_at) "
                "VALUES (:id, :name, true, NOW(), NOW())"
            ), {"id": ch_id, "name": ch_name})
        
        # Create candidate statuses
        print("📊 Aday durumları oluşturuluyor...")
        statuses_data = [
            ("status_1", "Başvurdu"),
            ("status_2", "İnceleme"),
            ("status_3", "Mülakat"),
            ("status_4", "Teklif"),
            ("status_5", "İşe Alındı"),
            ("status_6", "Reddedildi")
        ]
        
        for st_id, st_name in statuses_data:
            session.execute(text(
                "INSERT INTO candidate_statuses (id, name, is_active, created_at, updated_at) "
                "VALUES (:id, :name, true, NOW(), NOW())"
            ), {"id": st_id, "name": st_name})
        
        session.commit()
        print("✅ Lookup tabloları oluşturuldu")
        
        # Create candidates
        print("👥 20 aday oluşturuluyor...")
        for i in range(20):
            email = f"candidate{i+1}@example.com"
            first_name = fake.first_name()
            last_name = fake.last_name()
            
            # Random selection from valid values
            position = random.choice(positions_data)[1]
            position_id = random.choice(positions_data)[0]
            application_channel = random.choice(channels_data)[1]
            application_channel_id = random.choice(channels_data)[0]
            status = random.choice(statuses_data)[1]
            status_id = random.choice(statuses_data)[0]
            
            session.execute(text("""
                INSERT INTO candidates (
                    first_name, last_name, email, phone, position, position_id,
                    application_channel, application_channel_id, status, status_id,
                    application_date, hr_specialist, notes, is_active, created_at, updated_at
                ) VALUES (
                    :first_name, :last_name, :email, :phone, :position, :position_id,
                    :application_channel, :application_channel_id, :status, :status_id,
                    :application_date, :hr_specialist, :notes, true, NOW(), NOW()
                )
            """), {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": fake.phone_number()[:15],
                "position": position,
                "position_id": position_id,
                "application_channel": application_channel,
                "application_channel_id": application_channel_id,
                "status": status,
                "status_id": status_id,
                "application_date": fake.date_time_between(start_date='-6m', end_date='now'),
                "hr_specialist": fake.name(),
                "notes": fake.text(max_nb_chars=200)
            })
        
        session.commit()
        print("✅ 20 aday oluşturuldu")
        
        # Create interviews
        print("📅 20 mülakat oluşturuluyor...")
        
        # Get admin user
        admin_user = session.execute(text("SELECT id FROM users WHERE email = 'admin@hrats.com'")).fetchone()
        admin_id = admin_user[0] if admin_user else None
        
        for i in range(20):
            # Get random candidate
            candidate = session.execute(text("SELECT id FROM candidates ORDER BY RANDOM() LIMIT 1")).fetchone()
            candidate_id = candidate[0]
            
            # Generate interview date
            interview_date = fake.date_time_between(
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now() + timedelta(days=30)
            )
            
            start_datetime = interview_date.replace(
                hour=random.randint(9, 16),
                minute=random.choice([0, 15, 30, 45]),
                second=0,
                microsecond=0
            )
            
            end_datetime = start_datetime + timedelta(hours=random.randint(1, 3))
            
            meeting_types = ["in-person", "video", "phone"]
            statuses = ["scheduled", "completed", "cancelled", "rescheduled"]
            
            session.execute(text("""
                INSERT INTO interviews (
                    title, candidate_id, interviewer_id, interviewer_name,
                    start_datetime, end_datetime, status, meeting_type,
                    location, notes, is_active, created_at, updated_at, created_by
                ) VALUES (
                    :title, :candidate_id, :interviewer_id, :interviewer_name,
                    :start_datetime, :end_datetime, :status, :meeting_type,
                    :location, :notes, true, NOW(), NOW(), :created_by
                )
            """), {
                "title": f"Aday {i+1} - Mülakat",
                "candidate_id": candidate_id,
                "interviewer_id": admin_id,
                "interviewer_name": fake.name(),
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "status": random.choice(statuses),
                "meeting_type": random.choice(meeting_types),
                "location": fake.address()[:100] if random.choice([True, False]) else f"https://meet.google.com/{fake.word()}-{fake.word()}",
                "notes": fake.text(max_nb_chars=300),
                "created_by": admin_id
            })
        
        session.commit()
        print("✅ 20 mülakat oluşturuldu")
        
        # Print summary
        print("\n📊 Özet:")
        print(f"   👥 Aday sayısı: {session.execute(text('SELECT COUNT(*) FROM candidates')).scalar()}")
        print(f"   📅 Mülakat sayısı: {session.execute(text('SELECT COUNT(*) FROM interviews')).scalar()}")
        print(f"   🏢 Pozisyon sayısı: {session.execute(text('SELECT COUNT(*) FROM positions')).scalar()}")
        print(f"   📱 Başvuru kanalı sayısı: {session.execute(text('SELECT COUNT(*) FROM application_channels')).scalar()}")
        print(f"   📊 Aday durumu sayısı: {session.execute(text('SELECT COUNT(*) FROM candidate_statuses')).scalar()}")
        
        print("\n✅ Mock data başarıyla oluşturuldu!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    clear_and_create_data()