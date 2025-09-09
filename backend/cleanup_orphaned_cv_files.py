#!/usr/bin/env python3
"""
Cleanup script to remove orphaned CV files from disk
This script removes CV files that belong to deleted (soft deleted) candidates
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append('/app')

from app.db.session import get_db
from app.models.candidate import Candidate
from sqlalchemy.orm import Session

def cleanup_orphaned_cv_files():
    """Remove CV files that belong to deleted candidates"""
    try:
        db = next(get_db())
        
        # Get all deleted candidates
        deleted_candidates = db.query(Candidate).filter(Candidate.is_active == False).all()
        
        print(f"Found {len(deleted_candidates)} deleted candidates")
        
        deleted_files = []
        not_found_files = []
        error_files = []
        
        for candidate in deleted_candidates:
            if candidate.cv_file_path:
                file_path = f"/app{candidate.cv_file_path}"
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted_files.append(file_path)
                        print(f"✅ Deleted: {file_path}")
                    else:
                        not_found_files.append(file_path)
                        print(f"⚠️  Not found: {file_path}")
                except Exception as e:
                    error_files.append((file_path, str(e)))
                    print(f"❌ Error deleting {file_path}: {e}")
        
        print(f"\n📊 Summary:")
        print(f"✅ Successfully deleted: {len(deleted_files)} files")
        print(f"⚠️  Not found: {len(not_found_files)} files")
        print(f"❌ Errors: {len(error_files)} files")
        
        # Also clean up any files that don't have corresponding database entries
        cv_dir = "/app/uploads/cv"
        if os.path.exists(cv_dir):
            all_files = os.listdir(cv_dir)
            all_cv_paths = set()
            
            # Get all active CV file paths from database
            active_candidates = db.query(Candidate).filter(Candidate.is_active == True).all()
            for candidate in active_candidates:
                if candidate.cv_file_path:
                    filename = os.path.basename(candidate.cv_file_path)
                    all_cv_paths.add(filename)
            
            # Find orphaned files
            orphaned_files = []
            for file in all_files:
                if file not in all_cv_paths and file.endswith(('.pdf', '.doc', '.docx')):
                    orphaned_files.append(file)
            
            print(f"\n🔍 Found {len(orphaned_files)} orphaned files:")
            for file in orphaned_files:
                file_path = os.path.join(cv_dir, file)
                try:
                    os.remove(file_path)
                    print(f"🗑️  Deleted orphaned file: {file}")
                except Exception as e:
                    print(f"❌ Error deleting orphaned file {file}: {e}")
        
        print("\n✨ Cleanup completed!")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False
    
    return True

if __name__ == "__main__":
    cleanup_orphaned_cv_files()
