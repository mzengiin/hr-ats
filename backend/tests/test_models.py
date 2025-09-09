"""
Tests for database models
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid

from app.models.user import User
from app.models.user_role import UserRole
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog
from app.db.base import Base


@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
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


class TestUserModel:
    """Test User model functionality"""
    
    def test_create_user(self, db_session, sample_role):
        """Test creating a new user"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            role_id=sample_role.id
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.role_id == sample_role.id
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_relationship_with_role(self, db_session, sample_role):
        """Test user-role relationship"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            role_id=sample_role.id
        )
        db_session.add(user)
        db_session.commit()
        
        # Test relationship
        assert user.role.name == "hr_manager"
        assert user.role.permissions["candidates"] == ["read", "create", "update", "delete"]
    
    def test_user_email_unique(self, db_session, sample_role):
        """Test that email must be unique"""
        user1 = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            role_id=sample_role.id
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create another user with same email
        user2 = User(
            email="test@example.com",
            password_hash="another_password",
            first_name="Jane",
            last_name="Smith",
            role_id=sample_role.id
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()


class TestUserRoleModel:
    """Test UserRole model functionality"""
    
    def test_create_role(self, db_session):
        """Test creating a new user role"""
        role = UserRole(
            name="admin",
            description="System Administrator",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        
        assert role.id is not None
        assert role.name == "admin"
        assert role.description == "System Administrator"
        assert role.permissions["users"] == ["create", "read", "update", "delete"]
        assert role.created_at is not None
        assert role.updated_at is not None
    
    def test_role_name_unique(self, db_session):
        """Test that role name must be unique"""
        role1 = UserRole(
            name="admin",
            description="System Administrator",
            permissions={}
        )
        db_session.add(role1)
        db_session.commit()
        
        # Try to create another role with same name
        role2 = UserRole(
            name="admin",
            description="Another Admin",
            permissions={}
        )
        db_session.add(role2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()


class TestRefreshTokenModel:
    """Test RefreshToken model functionality"""
    
    def test_create_refresh_token(self, db_session, sample_role):
        """Test creating a refresh token"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            role_id=sample_role.id
        )
        db_session.add(user)
        db_session.commit()
        
        token = RefreshToken(
            user_id=user.id,
            token_hash="hashed_token",
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db_session.add(token)
        db_session.commit()
        
        assert token.id is not None
        assert token.user_id == user.id
        assert token.token_hash == "hashed_token"
        assert token.is_revoked is False
        assert token.created_at is not None
    
    def test_refresh_token_relationship_with_user(self, db_session, sample_role):
        """Test refresh token-user relationship"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            role_id=sample_role.id
        )
        db_session.add(user)
        db_session.commit()
        
        token = RefreshToken(
            user_id=user.id,
            token_hash="hashed_token",
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db_session.add(token)
        db_session.commit()
        
        # Test relationship
        assert token.user.email == "test@example.com"
        assert token.user.first_name == "John"
    
    def test_refresh_token_cascade_delete(self, db_session, sample_role):
        """Test that refresh tokens are deleted when user is deleted"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            role_id=sample_role.id
        )
        db_session.add(user)
        db_session.commit()
        
        token = RefreshToken(
            user_id=user.id,
            token_hash="hashed_token",
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db_session.add(token)
        db_session.commit()
        
        token_id = token.id
        
        # Delete user
        db_session.delete(user)
        db_session.commit()
        
        # Check that token is also deleted
        deleted_token = db_session.query(RefreshToken).filter(RefreshToken.id == token_id).first()
        assert deleted_token is None


class TestAuditLogModel:
    """Test AuditLog model functionality"""
    
    def test_create_audit_log(self, db_session, sample_role):
        """Test creating an audit log entry"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            role_id=sample_role.id
        )
        db_session.add(user)
        db_session.commit()
        
        audit_log = AuditLog(
            user_id=user.id,
            action="login",
            resource="auth",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={"login_method": "password"}
        )
        db_session.add(audit_log)
        db_session.commit()
        
        assert audit_log.id is not None
        assert audit_log.user_id == user.id
        assert audit_log.action == "login"
        assert audit_log.resource == "auth"
        assert audit_log.ip_address == "192.168.1.1"
        assert audit_log.user_agent == "Mozilla/5.0"
        assert audit_log.details["login_method"] == "password"
        assert audit_log.created_at is not None
    
    def test_audit_log_relationship_with_user(self, db_session, sample_role):
        """Test audit log-user relationship"""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            role_id=sample_role.id
        )
        db_session.add(user)
        db_session.commit()
        
        audit_log = AuditLog(
            user_id=user.id,
            action="login",
            resource="auth"
        )
        db_session.add(audit_log)
        db_session.commit()
        
        # Test relationship
        assert audit_log.user.email == "test@example.com"
        assert audit_log.user.first_name == "John"









