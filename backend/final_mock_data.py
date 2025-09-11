#!/usr/bin/env python3
"""
Final mock data insertion script for HR-ATS system
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.user_role import UserRole
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.models.position import Position
from app.models.application_channel import ApplicationChannel
from app.models.candidate_status import CandidateStatus
from app.core.security import get_password_hash

def create_database_session():
    """Create database session"""
    return SessionLocal()

def main():
    """Main function to run the mock data insertion"""
    print("Starting final mock data insertion...")
    
    session = create_database_session()
    
    try:
        # Check if we already have data
        existing_candidates = session.query(Candidate).count()
        if existing_candidates > 0:
            print(f"Found {existing_candidates} existing candidates. Skipping mock data insertion.")
            return
        
        # Create basic lookup data if not exists
        print("Creating basic lookup data...")
        
        # Positions
        positions_data = [
            {"id": "dev-senior", "name": "Senior Yazılım Geliştirici"},
            {"id": "dev-mid", "name": "Orta Seviye Yazılım Geliştirici"},
            {"id": "dev-junior", "name": "Junior Yazılım Geliştirici"},
            {"id": "frontend", "name": "Frontend Geliştirici"},
            {"id": "backend", "name": "Backend Geliştirici"},
            {"id": "fullstack", "name": "Full Stack Geliştirici"},
            {"id": "devops", "name": "DevOps Mühendisi"},
            {"id": "qa", "name": "QA Test Uzmanı"},
            {"id": "ui-ux", "name": "UI/UX Tasarımcı"},
            {"id": "data-scientist", "name": "Veri Bilimci"},
        ]
        
        for pos_data in positions_data:
            existing = session.query(Position).filter(Position.id == pos_data["id"]).first()
            if not existing:
                position = Position(**pos_data)
                session.add(position)
        
        # Application Channels
        channels_data = [
            {"id": "linkedin", "name": "LinkedIn"},
            {"id": "kariyer-net", "name": "Kariyer.net"},
            {"id": "referans", "name": "Referanslı"},
            {"id": "is-gorusmesi", "name": "İş Görüşmesi"},
            {"id": "universite", "name": "Üniversite"},
            {"id": "sosyal-medya", "name": "Sosyal Medya"},
            {"id": "web-sitesi", "name": "Web Sitesi"},
            {"id": "headhunter", "name": "Headhunter"},
            {"id": "diger", "name": "Diğer"},
        ]
        
        for channel_data in channels_data:
            existing = session.query(ApplicationChannel).filter(ApplicationChannel.id == channel_data["id"]).first()
            if not existing:
                channel = ApplicationChannel(**channel_data)
                session.add(channel)
        
        # Candidate Statuses
        statuses_data = [
            {"id": "basvurdu", "name": "Başvurdu"},
            {"id": "inceleme", "name": "İnceleme"},
            {"id": "mulakat-1", "name": "1. Mülakat"},
            {"id": "mulakat-2", "name": "2. Mülakat"},
            {"id": "teknik-test", "name": "Teknik Test"},
            {"id": "teklif", "name": "Teklif"},
            {"id": "ise-alindi", "name": "İşe Alındı"},
            {"id": "reddedildi", "name": "Reddedildi"},
            {"id": "beklemede", "name": "Beklemede"},
            {"id": "iptal", "name": "İptal"},
        ]
        
        for status_data in statuses_data:
            existing = session.query(CandidateStatus).filter(CandidateStatus.id == status_data["id"]).first()
            if not existing:
                status = CandidateStatus(**status_data)
                session.add(status)
        
        session.commit()
        print("Lookup data created successfully!")
        
        # Create user roles
        print("Creating user roles...")
        roles_data = [
            {
                "name": "admin",
                "description": "Sistem yöneticisi - tüm yetkiler",
                "permissions": {
                    "candidates": ["create", "read", "update", "delete"],
                    "interviews": ["create", "read", "update", "delete"],
                    "users": ["create", "read", "update", "delete"],
                    "reports": ["read"],
                    "settings": ["read", "update"]
                }
            },
            {
                "name": "ik_uzmani",
                "description": "İK Uzmanı - aday ve mülakat yönetimi",
                "permissions": {
                    "candidates": ["create", "read", "update"],
                    "interviews": ["create", "read", "update", "delete"],
                    "users": ["read"],
                    "reports": ["read"]
                }
            },
            {
                "name": "ik_uzman_yardimcisi",
                "description": "İK Uzman Yardımcısı - sınırlı yetkiler",
                "permissions": {
                    "candidates": ["create", "read"],
                    "interviews": ["create", "read"],
                    "users": ["read"]
                }
            }
        ]
        
        for role_data in roles_data:
            existing = session.query(UserRole).filter(UserRole.name == role_data["name"]).first()
            if not existing:
                role = UserRole(**role_data)
                session.add(role)
        
        session.commit()
        print("User roles created successfully!")
        
        # Create users
        print("Creating users...")
        admin_role = session.query(UserRole).filter(UserRole.name == "admin").first()
        ik_role = session.query(UserRole).filter(UserRole.name == "ik_uzmani").first()
        ik_yardimci_role = session.query(UserRole).filter(UserRole.name == "ik_uzman_yardimcisi").first()
        
        users_data = [
            {
                "first_name": "Admin",
                "last_name": "User",
                "email": "admin@hrats.com",
                "phone": "+90 555 000 0001",
                "role_id": admin_role.id,
                "is_active": True
            },
            {
                "first_name": "Ayşe",
                "last_name": "Yılmaz",
                "email": "ayse.yilmaz@hrats.com",
                "phone": "+90 555 000 0002",
                "role_id": ik_role.id,
                "is_active": True
            },
            {
                "first_name": "Mehmet",
                "last_name": "Demir",
                "email": "mehmet.demir@hrats.com",
                "phone": "+90 555 000 0003",
                "role_id": ik_role.id,
                "is_active": True
            },
            {
                "first_name": "Fatma",
                "last_name": "Kaya",
                "email": "fatma.kaya@hrats.com",
                "phone": "+90 555 000 0004",
                "role_id": ik_yardimci_role.id,
                "is_active": True
            },
            {
                "first_name": "Ali",
                "last_name": "Özkan",
                "email": "ali.ozkan@hrats.com",
                "phone": "+90 555 000 0005",
                "role_id": ik_yardimci_role.id,
                "is_active": True
            }
        ]
        
        for user_data in users_data:
            existing = session.query(User).filter(User.email == user_data["email"]).first()
            if not existing:
                user = User(
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    email=user_data["email"],
                    phone=user_data["phone"],
                    password_hash=get_password_hash("password123"),
                    role_id=user_data["role_id"],
                    is_active=user_data["is_active"]
                )
                session.add(user)
        
        session.commit()
        print("Users created successfully!")
        
        # Create 20 candidates with simple data
        print("Creating 20 candidates...")
        positions = session.query(Position).all()
        channels = session.query(ApplicationChannel).all()
        statuses = session.query(CandidateStatus).all()
        users = session.query(User).all()
        
        first_names = ['Ahmet', 'Mehmet', 'Ali', 'Veli', 'Ayşe', 'Fatma', 'Zeynep', 'Elif', 'Merve', 'Selin', 'Can', 'Deniz', 'Ece', 'Gökhan', 'Hakan', 'İpek', 'Jale', 'Kemal', 'Lale', 'Murat']
        last_names = ['Yılmaz', 'Kaya', 'Demir', 'Çelik', 'Şahin', 'Yıldız', 'Özkan', 'Arslan', 'Doğan', 'Kılıç', 'Aydın', 'Bozkurt', 'Ceylan', 'Duman', 'Erdoğan', 'Fidan', 'Güneş', 'Hızlı', 'İnce', 'Jandarma']
        
        # Valid status values according to constraint
        valid_statuses = ['Başvurdu', 'İnceleme', 'Mülakat', 'Teklif', 'İşe Alındı', 'Reddedildi', 'Aktif']
        valid_channels = ['LinkedIn', 'Kariyer.net', 'Referanslı', 'İş Görüşmesi', 'Diğer']
        
        candidates = []
        for i in range(20):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            
            selected_position = random.choice(positions)
            selected_channel = random.choice(channels)
            selected_status = random.choice(statuses)
            selected_user = random.choice(users)
            
            candidate = Candidate(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=f"+90 5{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
                position=selected_position.name,
                position_id=selected_position.id,
                application_channel=random.choice(valid_channels),
                application_channel_id=selected_channel.id,
                application_date=datetime.now() - timedelta(days=random.randint(1, 180)),
                hr_specialist=selected_user.full_name,
                hr_specialist_id=selected_user.id,
                status=random.choice(valid_statuses),
                status_id=selected_status.id,
                notes=f"Aday notları - {first_name} {last_name}",
                is_active=True
            )
            candidates.append(candidate)
        
        session.add_all(candidates)
        session.commit()
        print("20 candidates created successfully!")
        
        # Create 20 interviews
        print("Creating 20 interviews...")
        interviews = []
        
        for i in range(20):
            candidate = random.choice(candidates)
            interviewer = random.choice(users)
            
            # Random date in the next 30 days
            start_date = datetime.now() + timedelta(days=random.randint(1, 30), hours=random.randint(9, 17))
            duration = random.choice([30, 45, 60, 90, 120])
            end_date = start_date + timedelta(minutes=duration)
            
            # Random meeting type
            meeting_types = ['in-person', 'video', 'phone']
            meeting_type = random.choice(meeting_types)
            
            # Random status
            statuses_list = ['scheduled', 'completed', 'cancelled']
            status = random.choice(statuses_list)
            
            # Location based on meeting type
            if meeting_type == 'in-person':
                location = f"İstanbul, Beşiktaş - Ofis {random.randint(1, 10)}"
            elif meeting_type == 'video':
                location = f"https://zoom.us/j/{random.randint(100000000, 999999999)}"
            else:
                location = f"+90 {random.randint(500000000, 599999999)}"
            
            interview = Interview(
                title=f"{candidate.full_name} - {candidate.position} Mülakatı",
                candidate_id=candidate.id,
                interviewer_id=interviewer.id,
                interviewer_name=interviewer.full_name,
                start_datetime=start_date,
                end_datetime=end_date,
                status=status,
                meeting_type=meeting_type,
                location=location,
                notes=f"Mülakat notları - {candidate.full_name}",
                is_active=True,
                created_by=random.choice(users).id
            )
            interviews.append(interview)
        
        session.add_all(interviews)
        session.commit()
        print("20 interviews created successfully!")
        
        print("\n✅ Mock data insertion completed successfully!")
        print("\nCreated:")
        print("- 10 different positions")
        print("- 9 application channels")
        print("- 10 candidate statuses")
        print("- 3 user roles (admin, ik_uzmani, ik_uzman_yardimcisi)")
        print("- 5 users with different roles")
        print("- 20 candidates with diverse data")
        print("- 20 interviews with different dates and times")
        
        print("\nLogin credentials:")
        print("Admin: admin@hrats.com / password123")
        print("IK Uzmanı: ayse.yilmaz@hrats.com / password123")
        print("IK Uzman Yardımcısı: fatma.kaya@hrats.com / password123")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
