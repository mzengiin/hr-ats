#!/usr/bin/env python3
"""
Insert case study status data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models import CaseStudyStatus

# Database connection
DATABASE_URL = "postgresql://cvflow_user:cvflow_password@hr-ats-db-1:5432/cvflow_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def insert_case_study_statuses():
    """Insert case study statuses"""
    print("📊 Vaka çalışması durumları ekleniyor...")
    
    session = SessionLocal()
    
    try:
        # Clear existing data
        session.execute(text("DELETE FROM case_study_statuses"))
        
        # Case Study Statuses
        statuses_data = [
            ("status_1", "Beklemede"),
            ("status_2", "Devam Ediyor"),
            ("status_3", "Tamamlandı"),
            ("status_4", "İptal Edildi")
        ]
        
        for st_id, st_name in statuses_data:
            session.execute(text(
                "INSERT INTO case_study_statuses (id, name, is_active, created_at, updated_at) "
                "VALUES (:id, :name, true, NOW(), NOW())"
            ), {"id": st_id, "name": st_name})
        
        session.commit()
        print("✅ Vaka çalışması durumları eklendi")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    insert_case_study_statuses()
