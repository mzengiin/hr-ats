"""
Tests for File Upload API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.models.user import User
from app.models.user_role import UserRole
from app.models.cv_file import CVFile
from app.core.security import get_password_hash
from app.core.auth import get_current_user
import uuid
import os
import io


@pytest.fixture
def db_session():
    """Create a test database session with PostgreSQL"""
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/cvflow_test")
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    # Clean up before each test
    session.query(CVFile).delete()
    session.query(User).delete()
    session.query(UserRole).delete()
    session.commit()
    
    yield session
    session.close()


@pytest.fixture
def sample_role(db_session):
    """Create a sample user role"""
    role = UserRole(
        name="hr_manager",
        description="HR Manager",
        permissions={"candidates": ["read", "create", "update", "delete"]}
    )
    db_session.add(role)
    db_session.commit()
    return role


@pytest.fixture
def test_user(db_session, sample_role):
    """Create a test user"""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        first_name="Test",
        last_name="User",
        role_id=sample_role.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers"""
    # Login to get token
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    if response.status_code != 200:
        # If login fails, create a mock token for testing
        return {"Authorization": "Bearer mock_token_for_testing"}
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestFileUploadAPI:
    """Test File Upload API functionality"""
    
    @patch('app.core.auth.get_current_user')
    def test_upload_single_file_success(self, mock_get_current_user, client, test_user):
        """Test uploading a single CV file successfully"""
        mock_get_current_user.return_value = test_user
        
        # Create a test file
        test_file_content = b"Test PDF content"
        test_file = io.BytesIO(test_file_content)
        
        response = client.post(
            "/api/v1/files/upload",
            files={"files": ("test_cv.pdf", test_file, "application/pdf")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "uploaded_files" in data
        assert len(data["uploaded_files"]) == 1
        assert data["uploaded_files"][0]["original_filename"] == "test_cv.pdf"
        assert data["uploaded_files"][0]["mime_type"] == "application/pdf"
        assert data["total_files"] == 1
    
    def test_upload_multiple_files_success(self, client, auth_headers):
        """Test uploading multiple CV files successfully"""
        # Create test files
        files = []
        for i in range(3):
            content = f"Test PDF content {i}".encode()
            files.append(("files", (f"test_cv_{i}.pdf", io.BytesIO(content), "application/pdf")))
        
        response = client.post(
            "/api/v1/files/upload",
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["uploaded_files"]) == 3
        assert data["total_files"] == 3
    
    def test_upload_invalid_file_type(self, client, auth_headers):
        """Test uploading invalid file type"""
        test_file_content = b"Test content"
        test_file = io.BytesIO(test_file_content)
        
        response = client.post(
            "/api/v1/files/upload",
            files={"files": ("test.txt", test_file, "text/plain")},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]
    
    def test_upload_file_too_large(self, client, auth_headers):
        """Test uploading file that's too large"""
        # Create a large file (over 10MB)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        test_file = io.BytesIO(large_content)
        
        response = client.post(
            "/api/v1/files/upload",
            files={"files": ("large_file.pdf", test_file, "application/pdf")},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "File size exceeds" in response.json()["detail"]
    
    def test_upload_without_authentication(self, client):
        """Test uploading without authentication"""
        test_file_content = b"Test PDF content"
        test_file = io.BytesIO(test_file_content)
        
        response = client.post(
            "/api/v1/files/upload",
            files={"files": ("test_cv.pdf", test_file, "application/pdf")}
        )
        
        assert response.status_code == 403
    
    def test_upload_empty_file(self, client, auth_headers):
        """Test uploading empty file"""
        test_file = io.BytesIO(b"")
        
        response = client.post(
            "/api/v1/files/upload",
            files={"files": ("empty.pdf", test_file, "application/pdf")},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Empty file" in response.json()["detail"]


class TestFileManagementAPI:
    """Test File Management API functionality"""
    
    def test_list_user_files(self, client, auth_headers, db_session, test_user):
        """Test listing user's files"""
        # Create some test files
        for i in range(3):
            cv_file = CVFile(
                user_id=test_user.id,
                filename=f"test_cv_{i}.pdf",
                original_filename=f"Test CV {i}.pdf",
                file_path=f"/uploads/cv_files/test_cv_{i}.pdf",
                file_size=1024000,
                mime_type="application/pdf"
            )
            db_session.add(cv_file)
        db_session.commit()
        
        response = client.get("/api/v1/files", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert "pagination" in data
        assert len(data["files"]) == 3
    
    @patch('app.core.auth.get_current_user')
    def test_get_file_metadata(self, mock_get_current_user, client, db_session, test_user):
        """Test getting file metadata"""
        mock_get_current_user.return_value = test_user
        
        # Create a test file
        cv_file = CVFile(
            user_id=test_user.id,
            filename="test_cv.pdf",
            original_filename="Test CV.pdf",
            file_path="/uploads/cv_files/test_cv.pdf",
            file_size=1024000,
            mime_type="application/pdf"
        )
        db_session.add(cv_file)
        db_session.commit()
        db_session.refresh(cv_file)
        
        response = client.get(f"/api/v1/files/{cv_file.id}/metadata")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(cv_file.id)
        assert data["original_filename"] == "Test CV.pdf"
        assert data["file_size"] == 1024000
        assert data["mime_type"] == "application/pdf"
    
    @patch('app.core.auth.get_current_user')
    def test_delete_file(self, mock_get_current_user, client, db_session, test_user):
        """Test deleting a file"""
        mock_get_current_user.return_value = test_user
        
        # Create a test file
        cv_file = CVFile(
            user_id=test_user.id,
            filename="test_cv.pdf",
            original_filename="Test CV.pdf",
            file_path="/uploads/cv_files/test_cv.pdf",
            file_size=1024000,
            mime_type="application/pdf"
        )
        db_session.add(cv_file)
        db_session.commit()
        db_session.refresh(cv_file)
        
        response = client.delete(f"/api/v1/files/{cv_file.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "File deleted successfully" in data["message"]
        
        # Verify file is soft deleted
        deleted_file = db_session.query(CVFile).filter(CVFile.id == cv_file.id).first()
        assert deleted_file.is_active is False
    
    @patch('app.core.auth.get_current_user')
    def test_access_other_user_file(self, mock_get_current_user, client, db_session, sample_role, test_user):
        """Test accessing another user's file"""
        mock_get_current_user.return_value = test_user
        
        # Create another user
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("otherpass123"),
            first_name="Other",
            last_name="User",
            role_id=sample_role.id
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        
        # Create file for other user
        cv_file = CVFile(
            user_id=other_user.id,
            filename="other_cv.pdf",
            original_filename="Other CV.pdf",
            file_path="/uploads/cv_files/other_cv.pdf",
            file_size=1024000,
            mime_type="application/pdf"
        )
        db_session.add(cv_file)
        db_session.commit()
        db_session.refresh(cv_file)
        
        # Try to access other user's file
        response = client.get(f"/api/v1/files/{cv_file.id}/metadata")
        
        assert response.status_code == 404  # Should return 404 for file not found (not owned by user)
