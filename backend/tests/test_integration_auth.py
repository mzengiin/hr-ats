"""
End-to-end integration tests for complete authentication flow
"""
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.core.security import get_password_hash
from app.core.config import settings

# Test data
TEST_USER_DATA = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "password": "testpassword123"
}

TEST_ADMIN_DATA = {
    "first_name": "Admin",
    "last_name": "User",
    "email": "admin@example.com",
    "password": "adminpassword123"
}

class TestAuthenticationFlow:
    """Complete authentication flow integration tests"""
    
    @pytest.fixture
    async def client(self):
        """Create test client"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def db_session(self):
        """Create database session"""
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @pytest.fixture
    def test_user(self, db_session: Session):
        """Create test user"""
        # Create user role
        user_role = UserRole(
            name="user",
            description="Regular User",
            permissions={"users": ["read"]}
        )
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(user_role)
        
        # Create user
        user = User(
            first_name=TEST_USER_DATA["first_name"],
            last_name=TEST_USER_DATA["last_name"],
            email=TEST_USER_DATA["email"],
            hashed_password=get_password_hash(TEST_USER_DATA["password"]),
            role_id=user_role.id,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        return user
    
    @pytest.fixture
    def test_admin(self, db_session: Session):
        """Create test admin user"""
        # Create admin role
        admin_role = UserRole(
            name="admin",
            description="Administrator",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(admin_role)
        db_session.commit()
        db_session.refresh(admin_role)
        
        # Create admin user
        admin = User(
            first_name=TEST_ADMIN_DATA["first_name"],
            last_name=TEST_ADMIN_DATA["last_name"],
            email=TEST_ADMIN_DATA["email"],
            hashed_password=get_password_hash(TEST_ADMIN_DATA["password"]),
            role_id=admin_role.id,
            is_active=True
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        
        return admin
    
    async def test_complete_user_registration_flow(self, client: AsyncClient, db_session: Session):
        """Test complete user registration flow"""
        # 1. Register new user
        response = await client.post("/api/v1/auth/register", json=TEST_USER_DATA)
        assert response.status_code == 201
        user_data = response.json()
        assert user_data["email"] == TEST_USER_DATA["email"]
        assert "id" in user_data
        
        # 2. Verify user was created in database
        user = db_session.query(User).filter(User.email == TEST_USER_DATA["email"]).first()
        assert user is not None
        assert user.first_name == TEST_USER_DATA["first_name"]
        assert user.is_active is True
    
    async def test_complete_login_flow(self, client: AsyncClient, test_user: User):
        """Test complete login flow"""
        # 1. Login with valid credentials
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": TEST_USER_DATA["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        login_response = response.json()
        assert "access_token" in login_response
        assert "refresh_token" in login_response
        assert "token_type" in login_response
        assert "expires_in" in login_response
        assert "user" in login_response
        
        # 2. Verify user data in response
        user_data = login_response["user"]
        assert user_data["email"] == TEST_USER_DATA["email"]
        assert user_data["first_name"] == TEST_USER_DATA["first_name"]
        assert user_data["last_name"] == TEST_USER_DATA["last_name"]
        
        # 3. Test accessing protected endpoint with token
        headers = {"Authorization": f"Bearer {login_response['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        me_data = response.json()
        assert me_data["email"] == TEST_USER_DATA["email"]
    
    async def test_token_refresh_flow(self, client: AsyncClient, test_user: User):
        """Test token refresh flow"""
        # 1. Login to get tokens
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": TEST_USER_DATA["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        login_response = response.json()
        refresh_token = login_response["refresh_token"]
        
        # 2. Use refresh token to get new access token
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        refresh_response = response.json()
        assert "access_token" in refresh_response
        assert "token_type" in refresh_response
        assert "expires_in" in refresh_response
        assert refresh_response["token_type"] == "bearer"
        
        # 3. Verify new token works
        headers = {"Authorization": f"Bearer {refresh_response['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
    
    async def test_logout_flow(self, client: AsyncClient, test_user: User):
        """Test logout flow"""
        # 1. Login to get tokens
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": TEST_USER_DATA["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        login_response = response.json()
        access_token = login_response["access_token"]
        refresh_token = login_response["refresh_token"]
        
        # 2. Logout with refresh token
        logout_data = {"refresh_token": refresh_token}
        response = await client.delete("/api/v1/auth/logout", json=logout_data)
        assert response.status_code == 200
        
        # 3. Verify tokens are invalidated
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        
        # 4. Verify refresh token is invalidated
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 401
    
    async def test_password_change_flow(self, client: AsyncClient, test_user: User):
        """Test password change flow"""
        # 1. Login to get token
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": TEST_USER_DATA["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        login_response = response.json()
        access_token = login_response["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Change password
        password_data = {
            "current_password": TEST_USER_DATA["password"],
            "new_password": "newpassword123"
        }
        response = await client.post("/api/v1/auth/change-password", json=password_data, headers=headers)
        assert response.status_code == 200
        
        # 3. Verify old password doesn't work
        old_login_data = {
            "email": TEST_USER_DATA["email"],
            "password": TEST_USER_DATA["password"]
        }
        response = await client.post("/api/v1/auth/login", json=old_login_data)
        assert response.status_code == 401
        
        # 4. Verify new password works
        new_login_data = {
            "email": TEST_USER_DATA["email"],
            "password": "newpassword123"
        }
        response = await client.post("/api/v1/auth/login", json=new_login_data)
        assert response.status_code == 200
    
    async def test_invalid_credentials_flow(self, client: AsyncClient, test_user: User):
        """Test invalid credentials flow"""
        # 1. Login with wrong password
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": "wrongpassword"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        
        # 2. Login with non-existent email
        login_data = {
            "email": "nonexistent@example.com",
            "password": TEST_USER_DATA["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
    
    async def test_inactive_user_flow(self, client: AsyncClient, db_session: Session):
        """Test inactive user flow"""
        # 1. Create inactive user
        user_role = UserRole(
            name="user",
            description="Regular User",
            permissions={"users": ["read"]}
        )
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(user_role)
        
        inactive_user = User(
            first_name="Inactive",
            last_name="User",
            email="inactive@example.com",
            hashed_password=get_password_hash("password123"),
            role_id=user_role.id,
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        # 2. Try to login with inactive user
        login_data = {
            "email": "inactive@example.com",
            "password": "password123"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
    
    async def test_rate_limiting_flow(self, client: AsyncClient, test_user: User):
        """Test rate limiting flow"""
        # 1. Make multiple failed login attempts
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": "wrongpassword"
        }
        
        # Make 5 failed attempts (should trigger rate limiting)
        for i in range(5):
            response = await client.post("/api/v1/auth/login", json=login_data)
            assert response.status_code == 401
        
        # 2. Verify rate limiting is active
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 429  # Too Many Requests
    
    async def test_concurrent_login_flow(self, client: AsyncClient, test_user: User):
        """Test concurrent login flow"""
        # 1. Create multiple concurrent login requests
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": TEST_USER_DATA["password"]
        }
        
        # Create 10 concurrent login requests
        tasks = []
        for i in range(10):
            task = client.post("/api/v1/auth/login", json=login_data)
            tasks.append(task)
        
        # 2. Execute all requests concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 3. Verify all requests succeeded
        successful_responses = [r for r in responses if not isinstance(r, Exception) and r.status_code == 200]
        assert len(successful_responses) == 10
        
        # 4. Verify all tokens are valid
        for response in successful_responses:
            login_response = response.json()
            access_token = login_response["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            me_response = await client.get("/api/v1/auth/me", headers=headers)
            assert me_response.status_code == 200









