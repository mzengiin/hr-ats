#!/usr/bin/env python3
"""
Insert case study mock data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

# Database connection
DATABASE_URL = "postgresql://cvflow_user:cvflow_password@hr-ats-db-1:5432/cvflow_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def insert_case_study_mock_data():
    """Insert case study mock data"""
    print("📊 Vaka çalışması mock data ekleniyor...")
    
    session = SessionLocal()
    
    try:
        # Get candidates
        candidates = session.execute(text("SELECT id FROM candidates WHERE is_active = true LIMIT 10")).fetchall()
        if not candidates:
            print("❌ Hiç aday bulunamadı!")
            return
        
        # Case study titles
        titles = [
            "Frontend Geliştirici Rolü İçin Tasarım",
            "Backend API Geliştirme Vakası",
            "Veritabanı Optimizasyonu Projesi",
            "Mobil Uygulama Geliştirme",
            "E-ticaret Platformu Analizi",
            "Kullanıcı Deneyimi İyileştirmesi",
            "Güvenlik Testi ve Raporlama",
            "Performans Optimizasyonu",
            "Mikroservis Mimarisi Tasarımı",
            "DevOps Pipeline Kurulumu"
        ]
        
        descriptions = [
            "Bu vaka çalışmasında adayın frontend geliştirme becerilerini değerlendireceğiz.",
            "Backend API geliştirme konusundaki yetkinliğini test etmek için hazırlanmıştır.",
            "Veritabanı performansını artırmak için optimizasyon önerileri geliştirin.",
            "Mobil uygulama geliştirme sürecini ve en iyi uygulamaları gösterin.",
            "E-ticaret platformunun analizini yapın ve iyileştirme önerileri sunun.",
            "Kullanıcı deneyimini iyileştirmek için tasarım önerileri geliştirin.",
            "Güvenlik açıklarını tespit edin ve çözüm önerileri sunun.",
            "Sistem performansını artırmak için optimizasyon stratejileri geliştirin.",
            "Mikroservis mimarisi tasarımı ve implementasyonu yapın.",
            "CI/CD pipeline kurulumu ve otomasyon süreçlerini tasarlayın."
        ]
        
        statuses = ["Beklemede", "Devam Ediyor", "Tamamlandı", "İptal Edildi"]
        
        # Insert case studies
        for i in range(15):
            candidate = random.choice(candidates)
            title = random.choice(titles)
            description = random.choice(descriptions)
            status = random.choice(statuses)
            due_date = datetime.now() + timedelta(days=random.randint(1, 30))
            
            session.execute(text(
                "INSERT INTO case_studies (title, description, candidate_id, due_date, status, is_active, created_at, updated_at) "
                "VALUES (:title, :description, :candidate_id, :due_date, :status, true, NOW(), NOW())"
            ), {
                "title": title,
                "description": description,
                "candidate_id": candidate[0],
                "due_date": due_date,
                "status": status
            })
        
        session.commit()
        print("✅ Vaka çalışması mock data eklendi")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    insert_case_study_mock_data()
