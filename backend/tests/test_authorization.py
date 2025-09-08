"""
Tests for authorization and security functionality
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.db.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.core.security import get_password_hash


class TestRoleBasedAccessControl:
    """Test role-based access control functionality"""
    
    def test_admin_permissions(self, db_session: Session):
        """Test admin user has all permissions"""
        from app.core.auth import require_permission
        
        # Create admin role
        admin_role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={
                "users": ["create", "read", "update", "delete"],
                "candidates": ["create", "read", "update", "delete"],
                "interviews": ["create", "read", "update", "delete"],
                "offers": ["create", "read", "update", "delete"]
            }
        )
        db_session.add(admin_role)
        db_session.commit()
        db_session.refresh(admin_role)
        
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            password_hash=get_password_hash("admin_password_123"),
            first_name="Admin",
            last_name="User",
            role_id=admin_role.id
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        
        # Test admin permissions
        assert admin_user.role.name == "admin"
        assert "users" in admin_user.role.permissions
        assert "create" in admin_user.role.permissions["users"]
        assert "read" in admin_user.role.permissions["users"]
        assert "update" in admin_user.role.permissions["users"]
        assert "delete" in admin_user.role.permissions["users"]
    
    def test_hr_permissions(self, db_session: Session):
        """Test HR user has limited permissions"""
        # Create HR role
        hr_role = UserRole(
            name="hr",
            description="HR role",
            permissions={
                "candidates": ["create", "read", "update"],
                "interviews": ["create", "read", "update"],
                "offers": ["create", "read"]
            }
        )
        db_session.add(hr_role)
        db_session.commit()
        db_session.refresh(hr_role)
        
        # Create HR user
        hr_user = User(
            email="hr@example.com",
            password_hash=get_password_hash("hr_password_123"),
            first_name="HR",
            last_name="User",
            role_id=hr_role.id
        )
        db_session.add(hr_user)
        db_session.commit()
        db_session.refresh(hr_user)
        
        # Test HR permissions
        assert hr_user.role.name == "hr"
        assert "candidates" in hr_user.role.permissions
        assert "create" in hr_user.role.permissions["candidates"]
        assert "read" in hr_user.role.permissions["candidates"]
        assert "update" in hr_user.role.permissions["candidates"]
        assert "delete" not in hr_user.role.permissions["candidates"]
        assert "users" not in hr_user.role.permissions
    
    def test_viewer_permissions(self, db_session: Session):
        """Test viewer user has read-only permissions"""
        # Create viewer role
        viewer_role = UserRole(
            name="viewer",
            description="Viewer role",
            permissions={
                "candidates": ["read"],
                "interviews": ["read"],
                "offers": ["read"]
            }
        )
        db_session.add(viewer_role)
        db_session.commit()
        db_session.refresh(viewer_role)
        
        # Create viewer user
        viewer_user = User(
            email="viewer@example.com",
            password_hash=get_password_hash("viewer_password_123"),
            first_name="Viewer",
            last_name="User",
            role_id=viewer_role.id
        )
        db_session.add(viewer_user)
        db_session.commit()
        db_session.refresh(viewer_user)
        
        # Test viewer permissions
        assert viewer_user.role.name == "viewer"
        assert "candidates" in viewer_user.role.permissions
        assert "read" in viewer_user.role.permissions["candidates"]
        assert "create" not in viewer_user.role.permissions["candidates"]
        assert "update" not in viewer_user.role.permissions["candidates"]
        assert "delete" not in viewer_user.role.permissions["candidates"]
    
    def test_no_role_permissions(self, db_session: Session):
        """Test user with no role has no permissions"""
        # Create user without role
        user = User(
            email="norole@example.com",
            password_hash=get_password_hash("password_123"),
            first_name="No",
            last_name="Role",
            role_id=None
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test no permissions
        assert user.role is None
        assert user.role_id is None


class TestPermissionChecking:
    """Test permission checking functionality"""
    
    def test_check_permission_success(self, db_session: Session):
        """Test successful permission check"""
        from app.core.auth import require_permission
        
        # Create admin role
        admin_role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(admin_role)
        db_session.commit()
        db_session.refresh(admin_role)
        
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            password_hash=get_password_hash("admin_password_123"),
            first_name="Admin",
            last_name="User",
            role_id=admin_role.id
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        
        # Test permission check
        permission_checker = require_permission("users:create")
        result = permission_checker(admin_user)
        
        assert result == admin_user
    
    def test_check_permission_failure(self, db_session: Session):
        """Test failed permission check"""
        from app.core.auth import require_permission
        from fastapi import HTTPException
        
        # Create viewer role
        viewer_role = UserRole(
            name="viewer",
            description="Viewer role",
            permissions={"candidates": ["read"]}
        )
        db_session.add(viewer_role)
        db_session.commit()
        db_session.refresh(viewer_role)
        
        # Create viewer user
        viewer_user = User(
            email="viewer@example.com",
            password_hash=get_password_hash("viewer_password_123"),
            first_name="Viewer",
            last_name="User",
            role_id=viewer_role.id
        )
        db_session.add(viewer_user)
        db_session.commit()
        db_session.refresh(viewer_user)
        
        # Test permission check failure
        permission_checker = require_permission("users:create")
        
        with pytest.raises(HTTPException) as exc_info:
            permission_checker(viewer_user)
        
        assert exc_info.value.status_code == 403
        assert "Requires users:create permission" in str(exc_info.value.detail)
    
    def test_check_permission_no_role(self, db_session: Session):
        """Test permission check with no role"""
        from app.core.auth import require_permission
        from fastapi import HTTPException
        
        # Create user without role
        user = User(
            email="norole@example.com",
            password_hash=get_password_hash("password_123"),
            first_name="No",
            last_name="Role",
            role_id=None
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test permission check failure
        permission_checker = require_permission("users:read")
        
        with pytest.raises(HTTPException) as exc_info:
            permission_checker(user)
        
        assert exc_info.value.status_code == 403
        assert "No permissions assigned" in str(exc_info.value.detail)


class TestAuditLogging:
    """Test audit logging functionality"""
    
    def test_audit_log_creation(self, db_session: Session):
        """Test audit log creation"""
        from app.models.audit_log import AuditLog
        
        # Create audit log
        audit_log = AuditLog(
            user_id=uuid.uuid4(),
            action="LOGIN",
            resource_type="USER",
            resource_id=str(uuid.uuid4()),
            details={"ip_address": "127.0.0.1", "user_agent": "test"},
            ip_address="127.0.0.1",
            user_agent="test"
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)
        
        # Verify audit log
        assert audit_log.action == "LOGIN"
        assert audit_log.resource_type == "USER"
        assert audit_log.ip_address == "127.0.0.1"
        assert audit_log.user_agent == "test"
        assert audit_log.created_at is not None
    
    def test_audit_log_actions(self, db_session: Session):
        """Test different audit log actions"""
        from app.models.audit_log import AuditLog
        
        actions = [
            "LOGIN", "LOGOUT", "CREATE_USER", "UPDATE_USER",
            "DELETE_USER", "CREATE_CANDIDATE", "UPDATE_CANDIDATE",
            "CREATE_INTERVIEW", "UPDATE_INTERVIEW", "CREATE_OFFER"
        ]
        
        for action in actions:
            audit_log = AuditLog(
                user_id=uuid.uuid4(),
                action=action,
                resource_type="USER",
                resource_id=str(uuid.uuid4()),
                details={"test": "data"},
                ip_address="127.0.0.1",
                user_agent="test"
            )
            db_session.add(audit_log)
        
        db_session.commit()
        
        # Verify all actions were logged
        logged_actions = db_session.query(AuditLog.action).all()
        logged_action_names = [action[0] for action in logged_actions]
        
        for action in actions:
            assert action in logged_action_names


class TestSecurityHeaders:
    """Test security headers functionality"""
    
    def test_security_headers_middleware(self):
        """Test security headers middleware"""
        from app.core.middleware import SecurityHeadersMiddleware
        from fastapi import Request, Response
        
        # Mock request
        class MockRequest:
            def __init__(self):
                self.url = type('obj', (object,), {'scheme': 'https'})()
        
        request = MockRequest()
        
        # Create middleware
        middleware = SecurityHeadersMiddleware(None)
        
        # Mock response
        response = Response()
        
        # Test middleware
        result = middleware.dispatch(request, lambda: response)
        
        # Check security headers
        assert "X-Content-Type-Options" in result.headers
        assert "X-Frame-Options" in result.headers
        assert "X-XSS-Protection" in result.headers
        assert "Referrer-Policy" in result.headers
        assert "Permissions-Policy" in result.headers
        assert "Strict-Transport-Security" in result.headers
    
    def test_cors_middleware(self):
        """Test CORS middleware setup"""
        from app.core.middleware import setup_cors_middleware
        from fastapi import FastAPI
        
        app = FastAPI()
        setup_cors_middleware(app)
        
        # Check if CORS middleware is added
        assert len(app.middleware) > 0


class TestInputValidation:
    """Test input validation functionality"""
    
    def test_email_validation(self):
        """Test email validation"""
        from app.schemas.user import UserCreate
        from app.schemas.auth import LoginRequest
        
        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        for email in valid_emails:
            try:
                login_data = LoginRequest(email=email, password="password123")
                assert login_data.email == email
            except Exception as e:
                assert False, f"Valid email {email} failed validation: {e}"
        
        # Invalid emails
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            ""
        ]
        
        for email in invalid_emails:
            try:
                login_data = LoginRequest(email=email, password="password123")
                assert False, f"Invalid email {email} should have failed validation"
            except Exception as e:
                assert "Invalid email format" in str(e) or "value_error" in str(e).lower()
    
    def test_password_validation(self):
        """Test password validation"""
        from app.schemas.user import UserCreate
        
        # Valid passwords
        valid_passwords = [
            "SecurePassword123",
            "MyP@ssw0rd!",
            "StrongPwd2024"
        ]
        
        for password in valid_passwords:
            try:
                user_data = UserCreate(
                    email="test@example.com",
                    password=password,
                    first_name="Test",
                    last_name="User",
                    role_id=uuid.uuid4()
                )
                assert user_data.password == password
            except Exception as e:
                assert False, f"Valid password failed validation: {e}"
        
        # Invalid passwords
        invalid_passwords = [
            "123",  # Too short
            "password",  # No numbers
            "12345678",  # No letters
            "abcdefgh",  # No numbers
            ""  # Empty
        ]
        
        for password in invalid_passwords:
            try:
                user_data = UserCreate(
                    email="test@example.com",
                    password=password,
                    first_name="Test",
                    last_name="User",
                    role_id=uuid.uuid4()
                )
                assert False, f"Invalid password {password} should have failed validation"
            except Exception as e:
                assert "Password must be at least 8 characters" in str(e) or "value_error" in str(e).lower()


class TestSessionManagement:
    """Test session management functionality"""
    
    def test_token_expiration(self, db_session: Session):
        """Test token expiration"""
        from app.core.security import create_access_token, verify_token
        from datetime import datetime, timedelta
        
        # Create token with short expiration
        user_id = str(uuid.uuid4())
        token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(seconds=1)  # 1 second expiration
        )
        
        # Token should be valid initially
        token_data = verify_token(token)
        assert token_data.sub == user_id
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        # Token should be expired now
        try:
            verify_token(token)
            assert False, "Token should have expired"
        except Exception as e:
            assert "Token verification failed" in str(e) or "JWTError" in str(e)
    
    def test_refresh_token_rotation(self, db_session: Session):
        """Test refresh token rotation"""
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
            password_hash=get_password_hash("password_123"),
            first_name="Test",
            last_name="User",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create token service
        token_service = TokenService(db_session)
        
        # Create initial tokens
        tokens1 = token_service.create_tokens(user)
        refresh_token1 = tokens1["refresh_token"]
        
        # Refresh token
        new_tokens = token_service.refresh_access_token(refresh_token1)
        new_access_token = new_tokens["access_token"]
        
        # New access token should be different
        assert new_access_token != tokens1["access_token"]
        
        # New access token should be valid
        user_from_token = token_service.get_user_from_token(new_access_token)
        assert user_from_token is not None
        assert user_from_token.id == user.id


class TestSecurityIntegration:
    """Test security integration"""
    
    def test_complete_security_flow(self, db_session: Session):
        """Test complete security flow"""
        from app.services.auth_service import AuthService
        from app.services.token_service import TokenService
        from app.core.auth import require_permission
        
        # Create admin role
        admin_role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(admin_role)
        db_session.commit()
        db_session.refresh(admin_role)
        
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            password_hash=get_password_hash("admin_password_123"),
            first_name="Admin",
            last_name="User",
            role_id=admin_role.id
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        
        auth_service = AuthService(db_session)
        token_service = TokenService(db_session)
        
        # 1. Login
        login_result = auth_service.authenticate_user("admin@example.com", "admin_password_123")
        access_token = login_result["access_token"]
        
        # 2. Get user from token
        user_from_token = token_service.get_user_from_token(access_token)
        assert user_from_token is not None
        assert user_from_token.email == "admin@example.com"
        
        # 3. Check permissions
        permission_checker = require_permission("users:create")
        result = permission_checker(user_from_token)
        assert result == user_from_token
        
        # 4. Logout
        refresh_token = login_result["refresh_token"]
        logout_result = auth_service.logout(refresh_token)
        assert logout_result is True
        
        # 5. Verify token is revoked
        assert not token_service.validate_refresh_token(refresh_token)








