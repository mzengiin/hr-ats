"""
Tests for authentication API endpoints
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.db.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.core.security import get_password_hash


class TestLoginEndpoint:
    """Test login endpoint functionality"""
    
    def test_login_success(self, db_session: Session):
        """Test successful login"""
        from app.schemas.auth import LoginRequest
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Create a user
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("secure_password_123"),
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test login
        login_data = LoginRequest(
            email="test@example.com",
            password="secure_password_123"
        )
        
        from app.services.auth_service import AuthService
        auth_service = AuthService(db_session)
        result = auth_service.authenticate_user(login_data.email, login_data.password)
        
        assert result is not None
        assert "access_token" in result
        assert "refresh_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"
        assert "user" in result
        assert result["user"]["email"] == "test@example.com"
    
    def test_login_invalid_credentials(self, db_session: Session):
        """Test login with invalid credentials"""
        from app.schemas.auth import LoginRequest
        from app.services.auth_service import AuthService
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Create a user
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("secure_password_123"),
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()
        
        # Test invalid password
        auth_service = AuthService(db_session)
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            auth_service.authenticate_user("test@example.com", "wrong_password")
        
        # Test invalid email
        with pytest.raises(ValueError, match="Invalid credentials"):
            auth_service.authenticate_user("wrong@example.com", "secure_password_123")
    
    def test_login_inactive_user(self, db_session: Session):
        """Test login with inactive user"""
        from app.schemas.auth import LoginRequest
        from app.services.auth_service import AuthService
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Create an inactive user
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("secure_password_123"),
            first_name="John",
            last_name="Doe",
            role_id=role.id,
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        
        # Test login with inactive user
        auth_service = AuthService(db_session)
        
        with pytest.raises(ValueError, match="User account is inactive"):
            auth_service.authenticate_user("test@example.com", "secure_password_123")


class TestRefreshTokenEndpoint:
    """Test refresh token endpoint functionality"""
    
    def test_refresh_token_success(self, db_session: Session):
        """Test successful token refresh"""
        from app.services.auth_service import AuthService
        from app.services.token_service import TokenService
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Create a user
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("secure_password_123"),
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create tokens
        token_service = TokenService(db_session)
        tokens = token_service.create_tokens(user)
        refresh_token = tokens["refresh_token"]
        
        # Test refresh
        auth_service = AuthService(db_session)
        result = auth_service.refresh_access_token(refresh_token)
        
        assert result is not None
        assert "access_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"
        assert "expires_in" in result
    
    def test_refresh_token_invalid(self, db_session: Session):
        """Test refresh with invalid token"""
        from app.services.auth_service import AuthService
        
        auth_service = AuthService(db_session)
        
        with pytest.raises(ValueError, match="Invalid refresh token"):
            auth_service.refresh_access_token("invalid_token")
    
    def test_refresh_token_expired(self, db_session: Session):
        """Test refresh with expired token"""
        from app.services.auth_service import AuthService
        from app.core.security import create_refresh_token
        from datetime import datetime, timedelta
        
        # Create an expired refresh token
        expired_time = datetime.utcnow() - timedelta(hours=1)
        expired_token = create_refresh_token(
            data={"sub": str(uuid.uuid4())},
            expires_delta=timedelta(seconds=-3600)  # Expired 1 hour ago
        )
        
        auth_service = AuthService(db_session)
        
        with pytest.raises(ValueError, match="Invalid refresh token"):
            auth_service.refresh_access_token(expired_token)


class TestLogoutEndpoint:
    """Test logout endpoint functionality"""
    
    def test_logout_success(self, db_session: Session):
        """Test successful logout"""
        from app.services.auth_service import AuthService
        from app.services.token_service import TokenService
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Create a user
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("secure_password_123"),
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create tokens
        token_service = TokenService(db_session)
        tokens = token_service.create_tokens(user)
        refresh_token = tokens["refresh_token"]
        
        # Test logout
        auth_service = AuthService(db_session)
        result = auth_service.logout(refresh_token)
        
        assert result is True
        
        # Verify token is revoked
        assert not token_service.validate_refresh_token(refresh_token)
    
    def test_logout_invalid_token(self, db_session: Session):
        """Test logout with invalid token"""
        from app.services.auth_service import AuthService
        
        auth_service = AuthService(db_session)
        
        with pytest.raises(ValueError, match="Invalid refresh token"):
            auth_service.logout("invalid_token")
    
    def test_logout_already_revoked(self, db_session: Session):
        """Test logout with already revoked token"""
        from app.services.auth_service import AuthService
        from app.services.token_service import TokenService
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Create a user
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("secure_password_123"),
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create tokens
        token_service = TokenService(db_session)
        tokens = token_service.create_tokens(user)
        refresh_token = tokens["refresh_token"]
        
        # Revoke token first
        token_service.revoke_refresh_token(refresh_token)
        
        # Test logout with already revoked token
        auth_service = AuthService(db_session)
        
        with pytest.raises(ValueError, match="Invalid refresh token"):
            auth_service.logout(refresh_token)


class TestMeEndpoint:
    """Test me endpoint functionality"""
    
    def test_me_success(self, db_session: Session):
        """Test successful me endpoint"""
        from app.services.auth_service import AuthService
        from app.services.token_service import TokenService
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Create a user
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("secure_password_123"),
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create tokens
        token_service = TokenService(db_session)
        tokens = token_service.create_tokens(user)
        access_token = tokens["access_token"]
        
        # Test me endpoint
        auth_service = AuthService(db_session)
        result = auth_service.get_current_user_info(access_token)
        
        assert result is not None
        assert result["id"] == str(user.id)
        assert result["email"] == "test@example.com"
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["role"]["name"] == "admin"
    
    def test_me_invalid_token(self, db_session: Session):
        """Test me endpoint with invalid token"""
        from app.services.auth_service import AuthService
        
        auth_service = AuthService(db_session)
        
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.get_current_user_info("invalid_token")
    
    def test_me_expired_token(self, db_session: Session):
        """Test me endpoint with expired token"""
        from app.services.auth_service import AuthService
        from app.core.security import create_access_token
        from datetime import datetime, timedelta
        
        # Create an expired access token
        expired_time = datetime.utcnow() - timedelta(hours=1)
        expired_token = create_access_token(
            data={"sub": str(uuid.uuid4())},
            expires_delta=timedelta(seconds=-3600)  # Expired 1 hour ago
        )
        
        auth_service = AuthService(db_session)
        
        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.get_current_user_info(expired_token)


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_login_rate_limiting(self, db_session: Session):
        """Test rate limiting for login attempts"""
        from app.core.rate_limiter import check_rate_limit, reset_rate_limit
        from fastapi import Request
        
        # Mock request
        class MockRequest:
            def __init__(self):
                self.client = type('obj', (object,), {'host': '127.0.0.1'})()
                self.headers = {}
        
        request = MockRequest()
        
        # Test rate limiting
        for i in range(5):  # Default limit is 5 per minute
            try:
                check_rate_limit(request)
            except Exception as e:
                if i < 4:  # First 4 should pass
                    raise e
        
        # 6th attempt should be rate limited
        with pytest.raises(Exception):  # Should raise rate limit exception
            check_rate_limit(request)
        
        # Reset and test again
        reset_rate_limit(request)
        check_rate_limit(request)  # Should work again
    
    def test_login_attempt_tracking(self, db_session: Session):
        """Test login attempt tracking"""
        from app.core.rate_limiter import record_login_attempt, check_login_attempts
        
        email = "test@example.com"
        
        # Test failed attempts
        for i in range(4):
            record_login_attempt(email, success=False)
            assert not check_login_attempts(email)  # Should not be locked out yet
        
        # 5th failed attempt should lock out
        record_login_attempt(email, success=False)
        assert check_login_attempts(email)  # Should be locked out
        
        # Successful attempt should clear lockout
        record_login_attempt(email, success=True)
        assert not check_login_attempts(email)  # Should not be locked out


class TestAuthIntegration:
    """Test authentication integration"""
    
    def test_complete_auth_flow(self, db_session: Session):
        """Test complete authentication flow"""
        from app.services.auth_service import AuthService
        from app.services.token_service import TokenService
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Create a user
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("secure_password_123"),
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        auth_service = AuthService(db_session)
        token_service = TokenService(db_session)
        
        # 1. Login
        login_result = auth_service.authenticate_user("test@example.com", "secure_password_123")
        assert "access_token" in login_result
        assert "refresh_token" in login_result
        
        access_token = login_result["access_token"]
        refresh_token = login_result["refresh_token"]
        
        # 2. Get current user info
        user_info = auth_service.get_current_user_info(access_token)
        assert user_info["email"] == "test@example.com"
        
        # 3. Refresh token
        refresh_result = auth_service.refresh_access_token(refresh_token)
        assert "access_token" in refresh_result
        
        new_access_token = refresh_result["access_token"]
        
        # 4. Use new access token
        user_info_new = auth_service.get_current_user_info(new_access_token)
        assert user_info_new["email"] == "test@example.com"
        
        # 5. Logout
        logout_result = auth_service.logout(refresh_token)
        assert logout_result is True
        
        # 6. Verify token is revoked
        assert not token_service.validate_refresh_token(refresh_token)








