"""
Tests for user management API
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


class TestUserCreation:
    """Test user creation functionality"""
    
    def test_create_user_success(self, db_session: Session):
        """Test successful user creation"""
        from app.schemas.user import UserCreate
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Create user data
        user_data = UserCreate(
            email="test@example.com",
            password="secure_password_123",
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )
        
        # Create user
        from app.services.user_service import UserService
        user_service = UserService(db_session)
        user = user_service.create_user(user_data)
        
        # Verify user was created
        assert user is not None
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.role_id == role.id
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_create_user_duplicate_email(self, db_session: Session):
        """Test user creation with duplicate email fails"""
        from app.schemas.user import UserCreate
        from app.services.user_service import UserService
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Create first user
        user_data1 = UserCreate(
            email="test@example.com",
            password="secure_password_123",
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )
        
        user_service = UserService(db_session)
        user1 = user_service.create_user(user_data1)
        assert user1 is not None
        
        # Try to create second user with same email
        user_data2 = UserCreate(
            email="test@example.com",
            password="another_password_123",
            first_name="Jane",
            last_name="Smith",
            role_id=role.id
        )
        
        with pytest.raises(ValueError, match="Email already registered"):
            user_service.create_user(user_data2)
    
    def test_create_user_invalid_role(self, db_session: Session):
        """Test user creation with invalid role fails"""
        from app.schemas.user import UserCreate
        from app.services.user_service import UserService
        
        user_data = UserCreate(
            email="test@example.com",
            password="secure_password_123",
            first_name="John",
            last_name="Doe",
            role_id=uuid.uuid4()  # Non-existent role
        )
        
        user_service = UserService(db_session)
        
        with pytest.raises(ValueError, match="Role not found"):
            user_service.create_user(user_data)
    
    def test_create_user_password_validation(self, db_session: Session):
        """Test user creation with weak password fails"""
        from app.schemas.user import UserCreate
        from app.services.user_service import UserService
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Test weak password
        user_data = UserCreate(
            email="test@example.com",
            password="123",  # Too short
            first_name="John",
            last_name="Doe",
            role_id=role.id
        )
        
        user_service = UserService(db_session)
        
        with pytest.raises(ValueError, match="Password must be at least 8 characters"):
            user_service.create_user(user_data)


class TestUserRetrieval:
    """Test user retrieval functionality"""
    
    def test_get_user_by_id(self, db_session: Session):
        """Test getting user by ID"""
        from app.services.user_service import UserService
        
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
        
        # Get user by ID
        user_service = UserService(db_session)
        retrieved_user = user_service.get_user_by_id(user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.first_name == "John"
        assert retrieved_user.last_name == "Doe"
    
    def test_get_user_by_email(self, db_session: Session):
        """Test getting user by email"""
        from app.services.user_service import UserService
        
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
        
        # Get user by email
        user_service = UserService(db_session)
        retrieved_user = user_service.get_user_by_email("test@example.com")
        
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.first_name == "John"
        assert retrieved_user.last_name == "Doe"
    
    def test_get_user_not_found(self, db_session: Session):
        """Test getting non-existent user returns None"""
        from app.services.user_service import UserService
        
        user_service = UserService(db_session)
        
        # Try to get non-existent user
        user = user_service.get_user_by_id(uuid.uuid4())
        assert user is None
        
        user = user_service.get_user_by_email("nonexistent@example.com")
        assert user is None


class TestUserListing:
    """Test user listing functionality"""
    
    def test_list_users_pagination(self, db_session: Session):
        """Test user listing with pagination"""
        from app.services.user_service import UserService
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Create multiple users
        users = []
        for i in range(5):
            user = User(
                email=f"user{i}@example.com",
                password_hash=get_password_hash("secure_password_123"),
                first_name=f"User{i}",
                last_name="Test",
                role_id=role.id
            )
            db_session.add(user)
            users.append(user)
        
        db_session.commit()
        
        # Test pagination
        user_service = UserService(db_session)
        
        # First page
        result = user_service.list_users(skip=0, limit=2)
        assert len(result["users"]) == 2
        assert result["total"] == 5
        assert result["page"] == 1
        assert result["pages"] == 3
        
        # Second page
        result = user_service.list_users(skip=2, limit=2)
        assert len(result["users"]) == 2
        assert result["total"] == 5
        assert result["page"] == 2
        
        # Last page
        result = user_service.list_users(skip=4, limit=2)
        assert len(result["users"]) == 1
        assert result["total"] == 5
        assert result["page"] == 3
    
    def test_list_users_filtering(self, db_session: Session):
        """Test user listing with filtering"""
        from app.services.user_service import UserService
        
        # Create roles
        admin_role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        user_role = UserRole(
            name="user",
            description="Regular user role",
            permissions={"users": ["read"]}
        )
        db_session.add_all([admin_role, user_role])
        db_session.commit()
        db_session.refresh(admin_role)
        db_session.refresh(user_role)
        
        # Create users with different roles
        admin_user = User(
            email="admin@example.com",
            password_hash=get_password_hash("secure_password_123"),
            first_name="Admin",
            last_name="User",
            role_id=admin_role.id
        )
        regular_user = User(
            email="user@example.com",
            password_hash=get_password_hash("secure_password_123"),
            first_name="Regular",
            last_name="User",
            role_id=user_role.id
        )
        db_session.add_all([admin_user, regular_user])
        db_session.commit()
        
        # Test filtering by role
        user_service = UserService(db_session)
        
        # Filter by admin role
        result = user_service.list_users(role_id=admin_role.id)
        assert len(result["users"]) == 1
        assert result["users"][0].role_id == admin_role.id
        
        # Filter by user role
        result = user_service.list_users(role_id=user_role.id)
        assert len(result["users"]) == 1
        assert result["users"][0].role_id == user_role.id
        
        # Filter by active status
        regular_user.is_active = False
        db_session.commit()
        
        result = user_service.list_users(is_active=True)
        assert len(result["users"]) == 1
        assert result["users"][0].is_active is True
        
        result = user_service.list_users(is_active=False)
        assert len(result["users"]) == 1
        assert result["users"][0].is_active is False


class TestUserUpdate:
    """Test user update functionality"""
    
    def test_update_user_success(self, db_session: Session):
        """Test successful user update"""
        from app.schemas.user import UserUpdate
        from app.services.user_service import UserService
        
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
        
        # Update user
        update_data = UserUpdate(
            first_name="Jane",
            last_name="Smith"
        )
        
        user_service = UserService(db_session)
        updated_user = user_service.update_user(user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.first_name == "Jane"
        assert updated_user.last_name == "Smith"
        assert updated_user.email == "test@example.com"  # Email should not change
        assert updated_user.updated_at > user.updated_at
    
    def test_update_user_not_found(self, db_session: Session):
        """Test updating non-existent user fails"""
        from app.schemas.user import UserUpdate
        from app.services.user_service import UserService
        
        update_data = UserUpdate(first_name="Jane")
        user_service = UserService(db_session)
        
        with pytest.raises(ValueError, match="User not found"):
            user_service.update_user(uuid.uuid4(), update_data)
    
    def test_deactivate_user(self, db_session: Session):
        """Test user deactivation"""
        from app.services.user_service import UserService
        
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
        
        # Deactivate user
        user_service = UserService(db_session)
        deactivated_user = user_service.deactivate_user(user.id)
        
        assert deactivated_user is not None
        assert deactivated_user.is_active is False
        assert deactivated_user.updated_at > user.updated_at


class TestUserValidation:
    """Test user validation functionality"""
    
    def test_validate_email_format(self, db_session: Session):
        """Test email format validation"""
        from app.schemas.user import UserCreate
        from app.services.user_service import UserService
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Test invalid email formats
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            ""
        ]
        
        user_service = UserService(db_session)
        
        for invalid_email in invalid_emails:
            user_data = UserCreate(
                email=invalid_email,
                password="secure_password_123",
                first_name="John",
                last_name="Doe",
                role_id=role.id
            )
            
            with pytest.raises(ValueError, match="Invalid email format"):
                user_service.create_user(user_data)
    
    def test_validate_password_strength(self, db_session: Session):
        """Test password strength validation"""
        from app.schemas.user import UserCreate
        from app.services.user_service import UserService
        
        # Create a role first
        role = UserRole(
            name="admin",
            description="Administrator role",
            permissions={"users": ["create", "read", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        # Test weak passwords
        weak_passwords = [
            "123",  # Too short
            "password",  # Too common
            "12345678",  # Only numbers
            "abcdefgh",  # Only letters
            ""  # Empty
        ]
        
        user_service = UserService(db_session)
        
        for weak_password in weak_passwords:
            user_data = UserCreate(
                email="test@example.com",
                password=weak_password,
                first_name="John",
                last_name="Doe",
                role_id=role.id
            )
            
            with pytest.raises(ValueError, match="Password does not meet requirements"):
                user_service.create_user(user_data)


