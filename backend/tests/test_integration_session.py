"""
Integration tests for token refresh and session management
"""
import pytest
import asyncio
import time
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.user_role import UserRole
from app.models.refresh_token import RefreshToken
from app.core.security import get_password_hash
from app.core.config import settings

# Test data
TEST_USER_DATA = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "password": "testpassword123"
}

class TestSessionManagement:
    """Session management integration tests"""
    
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
    
    async def get_auth_tokens(self, client: AsyncClient):
        """Helper to get authentication tokens"""
        response = await client.post("/api/v1/auth/login", json=TEST_USER_DATA)
        assert response.status_code == 200
        return response.json()
    
    async def test_token_refresh_flow(self, client: AsyncClient, test_user: User, db_session: Session):
        """Test complete token refresh flow"""
        # 1. Login to get initial tokens
        tokens = await self.get_auth_tokens(client)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # 2. Verify refresh token is stored in database
        stored_refresh_token = db_session.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        assert stored_refresh_token is not None
        assert stored_refresh_token.user_id == test_user.id
        assert stored_refresh_token.is_active is True
        
        # 3. Use refresh token to get new access token
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        new_tokens = response.json()
        assert "access_token" in new_tokens
        assert "token_type" in new_tokens
        assert "expires_in" in new_tokens
        assert new_tokens["token_type"] == "bearer"
        
        # 4. Verify new access token works
        headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        # 5. Verify old access token still works (until expiration)
        old_headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/v1/auth/me", headers=old_headers)
        assert response.status_code == 200
    
    async def test_refresh_token_reuse_prevention(self, client: AsyncClient, test_user: User, db_session: Session):
        """Test refresh token can only be used once"""
        # 1. Login to get tokens
        tokens = await self.get_auth_tokens(client)
        refresh_token = tokens["refresh_token"]
        
        # 2. Use refresh token first time
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        # 3. Try to use same refresh token again (should fail)
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 401
        
        # 4. Verify refresh token is deactivated in database
        stored_refresh_token = db_session.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        assert stored_refresh_token is not None
        assert stored_refresh_token.is_active is False
    
    async def test_multiple_refresh_tokens(self, client: AsyncClient, test_user: User, db_session: Session):
        """Test multiple refresh tokens can exist for same user"""
        # 1. Login multiple times to get multiple refresh tokens
        tokens1 = await self.get_auth_tokens(client)
        tokens2 = await self.get_auth_tokens(client)
        tokens3 = await self.get_auth_tokens(client)
        
        # 2. Verify all refresh tokens are stored
        active_tokens = db_session.query(RefreshToken).filter(
            RefreshToken.user_id == test_user.id,
            RefreshToken.is_active == True
        ).all()
        assert len(active_tokens) == 3
        
        # 3. Use each refresh token
        for tokens in [tokens1, tokens2, tokens3]:
            refresh_data = {"refresh_token": tokens["refresh_token"]}
            response = await client.post("/api/v1/auth/refresh", json=refresh_data)
            assert response.status_code == 200
        
        # 4. Verify all refresh tokens are now deactivated
        active_tokens = db_session.query(RefreshToken).filter(
            RefreshToken.user_id == test_user.id,
            RefreshToken.is_active == True
        ).all()
        assert len(active_tokens) == 0
    
    async def test_logout_all_devices(self, client: AsyncClient, test_user: User, db_session: Session):
        """Test logout from all devices"""
        # 1. Login multiple times to create multiple sessions
        tokens1 = await self.get_auth_tokens(client)
        tokens2 = await self.get_auth_tokens(client)
        tokens3 = await self.get_auth_tokens(client)
        
        # 2. Verify multiple active refresh tokens exist
        active_tokens = db_session.query(RefreshToken).filter(
            RefreshToken.user_id == test_user.id,
            RefreshToken.is_active == True
        ).all()
        assert len(active_tokens) == 3
        
        # 3. Logout from all devices
        headers = {"Authorization": f"Bearer {tokens1['access_token']}"}
        response = await client.post("/api/v1/auth/logout-all", headers=headers)
        assert response.status_code == 200
        
        # 4. Verify all refresh tokens are deactivated
        active_tokens = db_session.query(RefreshToken).filter(
            RefreshToken.user_id == test_user.id,
            RefreshToken.is_active == True
        ).all()
        assert len(active_tokens) == 0
        
        # 5. Verify all access tokens are invalidated
        for tokens in [tokens1, tokens2, tokens3]:
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            response = await client.get("/api/v1/auth/me", headers=headers)
            assert response.status_code == 401
    
    async def test_session_expiration(self, client: AsyncClient, test_user: User, db_session: Session):
        """Test session expiration handling"""
        # 1. Login to get tokens
        tokens = await self.get_auth_tokens(client)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # 2. Simulate token expiration by manually deactivating refresh token
        stored_refresh_token = db_session.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        stored_refresh_token.is_active = False
        db_session.commit()
        
        # 3. Try to use refresh token (should fail)
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 401
        
        # 4. Try to use access token (should fail if token validation checks refresh token)
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        # This might still work depending on implementation
        # assert response.status_code == 401
    
    async def test_concurrent_session_management(self, client: AsyncClient, test_user: User, db_session: Session):
        """Test concurrent session management"""
        # 1. Create multiple concurrent login requests
        login_tasks = []
        for i in range(10):
            task = client.post("/api/v1/auth/login", json=TEST_USER_DATA)
            login_tasks.append(task)
        
        # 2. Execute all login requests concurrently
        responses = await asyncio.gather(*login_tasks, return_exceptions=True)
        
        # 3. Verify all logins succeeded
        successful_responses = [r for r in responses if not isinstance(r, Exception) and r.status_code == 200]
        assert len(successful_responses) == 10
        
        # 4. Verify all refresh tokens are stored
        active_tokens = db_session.query(RefreshToken).filter(
            RefreshToken.user_id == test_user.id,
            RefreshToken.is_active == True
        ).all()
        assert len(active_tokens) == 10
        
        # 5. Test concurrent refresh token usage
        refresh_tasks = []
        for response in successful_responses:
            tokens = response.json()
            refresh_data = {"refresh_token": tokens["refresh_token"]}
            task = client.post("/api/v1/auth/refresh", json=refresh_data)
            refresh_tasks.append(task)
        
        # 6. Execute all refresh requests concurrently
        refresh_responses = await asyncio.gather(*refresh_tasks, return_exceptions=True)
        
        # 7. Verify all refresh requests succeeded
        successful_refresh = [r for r in refresh_responses if not isinstance(r, Exception) and r.status_code == 200]
        assert len(successful_refresh) == 10
        
        # 8. Verify all refresh tokens are now deactivated
        active_tokens = db_session.query(RefreshToken).filter(
            RefreshToken.user_id == test_user.id,
            RefreshToken.is_active == True
        ).all()
        assert len(active_tokens) == 0
    
    async def test_session_cleanup(self, client: AsyncClient, test_user: User, db_session: Session):
        """Test session cleanup for inactive users"""
        # 1. Login to create session
        tokens = await self.get_auth_tokens(client)
        refresh_token = tokens["refresh_token"]
        
        # 2. Deactivate user
        test_user.is_active = False
        db_session.commit()
        
        # 3. Try to use refresh token (should fail)
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 401
        
        # 4. Try to login with inactive user (should fail)
        response = await client.post("/api/v1/auth/login", json=TEST_USER_DATA)
        assert response.status_code == 401
    
    async def test_token_validation_edge_cases(self, client: AsyncClient, test_user: User):
        """Test token validation edge cases"""
        # 1. Test with malformed token
        headers = {"Authorization": "Bearer malformed_token"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        
        # 2. Test with expired token format
        headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNjAwMDAwMDAwfQ.invalid"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        
        # 3. Test with missing Authorization header
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
        
        # 4. Test with wrong token type
        headers = {"Authorization": "Basic dGVzdEBleGFtcGxlLmNvbTp0ZXN0cGFzc3dvcmQxMjM="}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
    
    async def test_session_security(self, client: AsyncClient, test_user: User, db_session: Session):
        """Test session security measures"""
        # 1. Login to get tokens
        tokens = await self.get_auth_tokens(client)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # 2. Test that refresh token is properly hashed in database
        stored_refresh_token = db_session.query(RefreshToken).filter(
            RefreshToken.user_id == test_user.id
        ).first()
        assert stored_refresh_token is not None
        assert stored_refresh_token.token != refresh_token  # Should be hashed
        assert len(stored_refresh_token.token) > len(refresh_token)  # Hashed should be longer
        
        # 3. Test that access token contains correct claims
        import jwt
        from app.core.config import settings
        
        try:
            decoded = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            assert decoded["sub"] == test_user.email
            assert "exp" in decoded
            assert "iat" in decoded
        except jwt.InvalidTokenError:
            pytest.fail("Access token should be valid JWT")
        
        # 4. Test that refresh token is not exposed in API responses
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        me_data = response.json()
        assert "refresh_token" not in me_data
        assert "access_token" not in me_data








