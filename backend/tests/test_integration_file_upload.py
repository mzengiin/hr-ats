"""
Integration tests for file upload system
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.models.user import User
from app.models.user_role import UserRole
from app.models.cv_file import CVFile
from app.core.security import get_password_hash
import uuid
import os
import io


@pytest.fixture
def db_session():
    """Create a test database session"""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_role(db_session):
    """Create a sample role"""
    role = UserRole(
        name="hr_manager",
        description="HR Manager",
        permissions=["files:read", "files:write", "files:delete"]
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
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


class TestFileUploadIntegration:
    """Integration tests for complete file upload flow"""
    
    def test_complete_file_upload_flow(self, client, db_session, test_user):
        """Test complete file upload workflow"""
        # Step 1: Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Upload file
        test_file_content = b"Test PDF content for integration test"
        test_file = io.BytesIO(test_file_content)
        
        upload_response = client.post(
            "/api/v1/files/upload",
            files={"files": ("integration_test.pdf", test_file, "application/pdf")},
            headers=headers
        )
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        assert "uploaded_files" in upload_data
        assert len(upload_data["uploaded_files"]) == 1
        
        file_id = upload_data["uploaded_files"][0]["id"]
        
        # Step 3: List files
        list_response = client.get("/api/v1/files/list", headers=headers)
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert "files" in list_data
        assert len(list_data["files"]) == 1
        assert list_data["files"][0]["id"] == file_id
        
        # Step 4: Get file metadata
        metadata_response = client.get(f"/api/v1/files/{file_id}/metadata", headers=headers)
        assert metadata_response.status_code == 200
        metadata = metadata_response.json()
        assert metadata["id"] == file_id
        assert metadata["original_filename"] == "integration_test.pdf"
        
        # Step 5: Download file
        download_response = client.get(f"/api/v1/files/{file_id}", headers=headers)
        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "application/pdf"
        
        # Step 6: Delete file
        delete_response = client.delete(f"/api/v1/files/{file_id}", headers=headers)
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert "File deleted successfully" in delete_data["message"]
        
        # Step 7: Verify file is deleted
        verify_response = client.get(f"/api/v1/files/{file_id}/metadata", headers=headers)
        assert verify_response.status_code == 404
    
    def test_file_upload_with_validation_errors(self, client, db_session, test_user):
        """Test file upload with various validation errors"""
        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 1: Invalid file type
        invalid_file = io.BytesIO(b"Not a PDF file")
        response = client.post(
            "/api/v1/files/upload",
            files={"files": ("test.txt", invalid_file, "text/plain")},
            headers=headers
        )
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]
        
        # Test 2: Empty file
        empty_file = io.BytesIO(b"")
        response = client.post(
            "/api/v1/files/upload",
            files={"files": ("empty.pdf", empty_file, "application/pdf")},
            headers=headers
        )
        assert response.status_code == 400
        assert "Empty file not allowed" in response.json()["detail"]
        
        # Test 3: File too large (simulate)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        large_file = io.BytesIO(large_content)
        response = client.post(
            "/api/v1/files/upload",
            files={"files": ("large.pdf", large_file, "application/pdf")},
            headers=headers
        )
        assert response.status_code == 400
        assert "File size exceeds" in response.json()["detail"]
    
    def test_file_security_validation(self, client, db_session, test_user):
        """Test file security validation"""
        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test suspicious content
        suspicious_content = b"<script>alert('xss')</script>"
        suspicious_file = io.BytesIO(suspicious_content)
        response = client.post(
            "/api/v1/files/upload",
            files={"files": ("suspicious.pdf", suspicious_file, "application/pdf")},
            headers=headers
        )
        assert response.status_code == 400
        assert "suspicious content" in response.json()["detail"]
    
    def test_multiple_file_upload(self, client, db_session, test_user):
        """Test uploading multiple files at once"""
        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload multiple files
        files = []
        for i in range(3):
            content = f"Test PDF content {i}".encode()
            files.append(("test_file_{}.pdf".format(i), io.BytesIO(content), "application/pdf"))
        
        response = client.post(
            "/api/v1/files/upload",
            files=[("files", file[0], file[2]) for file in files],
            headers=headers
        )
        assert response.status_code == 200
        upload_data = response.json()
        assert len(upload_data["uploaded_files"]) == 3
        assert upload_data["total_files"] == 3
        
        # Verify all files are listed
        list_response = client.get("/api/v1/files/list", headers=headers)
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert len(list_data["files"]) == 3
