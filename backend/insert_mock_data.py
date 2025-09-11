#!/usr/bin/env python3
"""
Mock data insertion script for HR-ATS system
Creates 20 candidates, 20 interviews, and various users with different roles
"""

import sys
import os
from datetime import datetime, timedelta
import random
import uuid

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Try to import faker, if not available, use fallback
try:
    from faker import Faker
    fake = Faker('tr_TR')
except ImportError:
    # Fallback data if faker is not available
    class FakeData:
        def first_name(self):
            names = ['Ahmet', 'Mehmet', 'Ali', 'Veli', 'Ayşe', 'Fatma', 'Zeynep', 'Elif', 'Merve', 'Selin']
            return random.choice(names)
        
        def last_name(self):
            surnames = ['Yılmaz', 'Kaya', 'Demir', 'Çelik', 'Şahin', 'Yıldız', 'Özkan', 'Arslan', 'Doğan', 'Kılıç']
            return random.choice(surnames)
        
        def email(self):
            return f"{self.first_name().lower()}.{self.last_name().lower()}@example.com"
        
        def phone_number(self):
            return f"+90 5{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
        
        def date_time_between(self, start_date, end_date):
            start = datetime.strptime(start_date, '%Y-%m-%d') if isinstance(start_date, str) else start_date
            end = datetime.strptime(end_date, '%Y-%m-%d') if isinstance(end_date, str) else end_date
            delta = end - start
            random_days = random.randint(0, delta.days)
            return start + timedelta(days=random_days)
        
        def text(self, max_nb_chars=200):
            texts = [
                "Deneyimli yazılım geliştirici aranıyor.",
                "Takım çalışmasına uygun, dinamik kişilik.",
                "Problem çözme yeteneği yüksek.",
                "İletişim becerileri güçlü.",
                "Sürekli öğrenmeye açık.",
                "Proaktif yaklaşım sergileyen.",
                "Detaylara önem veren.",
                "Yaratıcı düşünce yapısına sahip."
            ]
            return random.choice(texts)
        
        def address(self):
            addresses = [
                "İstanbul, Beşiktaş",
                "Ankara, Çankaya", 
                "İzmir, Konak",
                "Bursa, Osmangazi",
                "Antalya, Muratpaşa"
            ]
            return random.choice(addresses)
        
        def random_int(self, min=100000000, max=999999999):
            return random.randint(min, max)
    
    fake = FakeData()

from app.db.session import SessionLocal
from app.models.user import User
from app.models.user_role import UserRole
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.models.position import Position
from app.models.application_channel import ApplicationChannel
from app.models.candidate_status import CandidateStatus
from app.core.security import get_password_hash

# Initialize Faker (already done above)

def create_database_session():
    """Create database session"""
    return SessionLocal()

def insert_lookup_data(session):
    """Insert lookup table data"""
    print("Inserting lookup data...")
    
    # Positions
    positions = [
        {"id": "dev-senior", "name": "Senior Yazılım Geliştirici", "description": "Deneyimli yazılım geliştirici"},
        {"id": "dev-mid", "name": "Orta Seviye Yazılım Geliştirici", "description": "Orta seviye yazılım geliştirici"},
        {"id": "dev-junior", "name": "Junior Yazılım Geliştirici", "description": "Yeni başlayan yazılım geliştirici"},
        {"id": "frontend", "name": "Frontend Geliştirici", "description": "React, Vue, Angular uzmanı"},
        {"id": "backend", "name": "Backend Geliştirici", "description": "Node.js, Python, Java uzmanı"},
        {"id": "fullstack", "name": "Full Stack Geliştirici", "description": "Hem frontend hem backend"},
        {"id": "devops", "name": "DevOps Mühendisi", "description": "CI/CD, Docker, Kubernetes uzmanı"},
        {"id": "qa", "name": "QA Test Uzmanı", "description": "Kalite güvence ve test uzmanı"},
        {"id": "ui-ux", "name": "UI/UX Tasarımcı", "description": "Kullanıcı arayüzü tasarımcısı"},
        {"id": "data-scientist", "name": "Veri Bilimci", "description": "Machine Learning ve veri analizi"},
        {"id": "product-manager", "name": "Ürün Müdürü", "description": "Ürün stratejisi ve yönetimi"},
        {"id": "project-manager", "name": "Proje Müdürü", "description": "Proje yönetimi ve koordinasyon"},
        {"id": "hr-specialist", "name": "İK Uzmanı", "description": "İnsan kaynakları uzmanı"},
        {"id": "marketing", "name": "Pazarlama Uzmanı", "description": "Dijital pazarlama ve reklam"},
        {"id": "sales", "name": "Satış Uzmanı", "description": "Müşteri ilişkileri ve satış"},
    ]
    
    for pos_data in positions:
        existing = session.query(Position).filter(Position.id == pos_data["id"]).first()
        if not existing:
            position = Position(**pos_data)
            session.add(position)
    
    # Application Channels
    channels = [
        {"id": "linkedin", "name": "LinkedIn", "description": "LinkedIn üzerinden başvuru"},
        {"id": "kariyer-net", "name": "Kariyer.net", "description": "Kariyer.net platformu"},
        {"id": "referans", "name": "Referanslı", "description": "Çalışan referansı"},
        {"id": "is-gorusmesi", "name": "İş Görüşmesi", "description": "Doğrudan iş görüşmesi"},
        {"id": "universite", "name": "Üniversite", "description": "Üniversite kariyer fuarları"},
        {"id": "sosyal-medya", "name": "Sosyal Medya", "description": "Facebook, Instagram, Twitter"},
        {"id": "web-sitesi", "name": "Web Sitesi", "description": "Şirket web sitesi"},
        {"id": "headhunter", "name": "Headhunter", "description": "İK danışmanlık firması"},
        {"id": "diger", "name": "Diğer", "description": "Diğer kanallar"},
    ]
    
    for channel_data in channels:
        existing = session.query(ApplicationChannel).filter(ApplicationChannel.id == channel_data["id"]).first()
        if not existing:
            channel = ApplicationChannel(**channel_data)
            session.add(channel)
    
    # Candidate Statuses
    statuses = [
        {"id": "basvurdu", "name": "Başvurdu", "description": "İlk başvuru yapıldı"},
        {"id": "inceleme", "name": "İnceleme", "description": "CV inceleniyor"},
        {"id": "mulakat-1", "name": "1. Mülakat", "description": "İlk mülakat aşaması"},
        {"id": "mulakat-2", "name": "2. Mülakat", "description": "İkinci mülakat aşaması"},
        {"id": "teknik-test", "name": "Teknik Test", "description": "Teknik değerlendirme"},
        {"id": "teklif", "name": "Teklif", "description": "İş teklifi verildi"},
        {"id": "ise-alindi", "name": "İşe Alındı", "description": "Başarıyla işe alındı"},
        {"id": "reddedildi", "name": "Reddedildi", "description": "Başvuru reddedildi"},
        {"id": "beklemede", "name": "Beklemede", "description": "Bekleme listesinde"},
        {"id": "iptal", "name": "İptal", "description": "Aday tarafından iptal edildi"},
    ]
    
    for status_data in statuses:
        existing = session.query(CandidateStatus).filter(CandidateStatus.id == status_data["id"]).first()
        if not existing:
            status = CandidateStatus(**status_data)
            session.add(status)
    
    session.commit()
    print("Lookup data inserted successfully!")

def create_user_roles(session):
    """Create user roles with different permissions"""
    print("Creating user roles...")
    
    roles = [
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
    
    for role_data in roles:
        role = UserRole(**role_data)
        session.merge(role)
    
    session.commit()
    print("User roles created successfully!")

def create_users(session):
    """Create users with different roles"""
    print("Creating users...")
    
    # Get role IDs
    admin_role = session.query(UserRole).filter(UserRole.name == "admin").first()
    ik_role = session.query(UserRole).filter(UserRole.name == "ik_uzmani").first()
    ik_yardimci_role = session.query(UserRole).filter(UserRole.name == "ik_uzman_yardimcisi").first()
    
    users = [
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
    
    for user_data in users:
        user = User(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            phone=user_data["phone"],
            hashed_password=get_password_hash("password123"),
            role_id=user_data["role_id"],
            is_active=user_data["is_active"]
        )
        session.merge(user)
    
    session.commit()
    print("Users created successfully!")

def create_candidates(session):
    """Create 20 mock candidates"""
    print("Creating 20 candidates...")
    
    # Get lookup data
    positions = session.query(Position).all()
    channels = session.query(ApplicationChannel).all()
    statuses = session.query(CandidateStatus).all()
    users = session.query(User).all()
    
    candidates = []
    
    for i in range(20):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        
        candidate = Candidate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=fake.phone_number(),
            position=random.choice(positions).name,
            position_id=random.choice(positions).id,
            application_channel=random.choice(channels).name,
            application_channel_id=random.choice(channels).id,
            application_date=fake.date_time_between(start_date='-6M', end_date='now'),
            hr_specialist=random.choice(users).full_name,
            hr_specialist_id=random.choice(users).id,
            status=random.choice(statuses).name,
            status_id=random.choice(statuses).id,
            notes=fake.text(max_nb_chars=200),
            is_active=True
        )
        candidates.append(candidate)
    
    session.add_all(candidates)
    session.commit()
    print("20 candidates created successfully!")

def create_interviews(session):
    """Create 20 mock interviews with different dates"""
    print("Creating 20 interviews...")
    
    candidates = session.query(Candidate).all()
    users = session.query(User).all()
    
    interviews = []
    
    # Create interviews for the next 30 days
    for i in range(20):
        candidate = random.choice(candidates)
        interviewer = random.choice(users)
        
        # Random date in the next 30 days
        start_date = fake.date_time_between(start_date='now', end_date='+30d')
        # Random duration between 30 minutes and 2 hours
        duration = random.choice([30, 45, 60, 90, 120])
        end_date = start_date + timedelta(minutes=duration)
        
        # Random meeting type
        meeting_types = ['in-person', 'video', 'phone']
        meeting_type = random.choice(meeting_types)
        
        # Random status
        statuses = ['scheduled', 'completed', 'cancelled']
        status = random.choice(statuses)
        
        # Location based on meeting type
        if meeting_type == 'in-person':
            location = fake.address()
        elif meeting_type == 'video':
            location = f"https://zoom.us/j/{fake.random_int(min=100000000, max=999999999)}"
        else:
            location = f"+90 {fake.random_int(min=500000000, max=599999999)}"
        
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
            notes=fake.text(max_nb_chars=300),
            is_active=True,
            created_by=random.choice(users).id
        )
        interviews.append(interview)
    
    session.add_all(interviews)
    session.commit()
    print("20 interviews created successfully!")

def main():
    """Main function to run the mock data insertion"""
    print("Starting mock data insertion...")
    
    session = create_database_session()
    
    try:
        # Insert lookup data first
        insert_lookup_data(session)
        
        # Create user roles
        create_user_roles(session)
        
        # Create users
        create_users(session)
        
        # Create candidates
        create_candidates(session)
        
        # Create interviews
        create_interviews(session)
        
        print("\n✅ Mock data insertion completed successfully!")
        print("\nCreated:")
        print("- 15 different positions")
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
