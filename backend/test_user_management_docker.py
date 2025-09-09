"""
Comprehensive test for user management using Docker environment
"""
import os
import sys
import asyncio
from datetime import datetime
import uuid

# Add the app directory to the Python path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test that all user management modules can be imported"""
    print("🧪 Testing user management imports...")
    
    try:
        from app.schemas.user import (
            UserCreate, UserUpdate, UserResponse, UserListResponse,
            UserWithRoleResponse, PasswordChange, UserFilter
        )
        from app.services.user_service import UserService
        from app.api.v1.users import router
        from app.core.exceptions import (
            ValidationError, NotFoundError, AuthenticationError,
            AuthorizationError, DuplicateError, BusinessLogicError
        )
        print("✅ All user management modules imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_user_schemas():
    """Test user schema validation"""
    print("🧪 Testing user schemas...")
    
    try:
        from app.schemas.user import UserCreate, UserUpdate, PasswordChange
        
        # Test UserCreate validation
        user_data = UserCreate(
            email="test@example.com",
            password="secure_password_123",
            first_name="John",
            last_name="Doe",
            role_id=uuid.uuid4()
        )
        
        assert user_data.email == "test@example.com"
        assert user_data.first_name == "John"
        assert user_data.last_name == "Doe"
        
        # Test UserUpdate validation
        update_data = UserUpdate(
            first_name="Jane",
            last_name="Smith"
        )
        
        assert update_data.first_name == "Jane"
        assert update_data.last_name == "Smith"
        
        # Test PasswordChange validation
        password_data = PasswordChange(
            current_password="old_password_123",
            new_password="new_password_123"
        )
        
        assert password_data.current_password == "old_password_123"
        assert password_data.new_password == "new_password_123"
        
        print("✅ User schemas work correctly!")
        return True
    except Exception as e:
        print(f"❌ User schemas test failed: {e}")
        return False

def test_user_service_creation():
    """Test user service creation"""
    print("🧪 Testing user service creation...")
    
    try:
        from app.services.user_service import UserService
        from app.db.session import get_db
        
        # Get database session
        db = next(get_db())
        
        # Create user service
        user_service = UserService(db)
        
        assert user_service is not None
        assert user_service.db == db
        
        print("✅ User service creation works correctly!")
        return True
    except Exception as e:
        print(f"❌ User service creation test failed: {e}")
        return False

def test_user_validation():
    """Test user validation logic"""
    print("🧪 Testing user validation...")
    
    try:
        from app.schemas.user import UserCreate
        
        # Test valid user data
        valid_user = UserCreate(
            email="test@example.com",
            password="secure_password_123",
            first_name="John",
            last_name="Doe",
            role_id=uuid.uuid4()
        )
        
        assert valid_user.email == "test@example.com"
        assert valid_user.first_name == "John"
        assert valid_user.last_name == "Doe"
        
        # Test invalid email format
        try:
            invalid_user = UserCreate(
                email="invalid-email",
                password="secure_password_123",
                first_name="John",
                last_name="Doe",
                role_id=uuid.uuid4()
            )
            assert False, "Should have raised validation error"
        except Exception as e:
            assert "Invalid email format" in str(e) or "value_error" in str(e).lower()
        
        # Test weak password
        try:
            weak_password_user = UserCreate(
                email="test@example.com",
                password="123",
                first_name="John",
                last_name="Doe",
                role_id=uuid.uuid4()
            )
            assert False, "Should have raised validation error"
        except Exception as e:
            assert "Password must be at least 8 characters" in str(e) or "value_error" in str(e).lower()
        
        print("✅ User validation works correctly!")
        return True
    except Exception as e:
        print(f"❌ User validation test failed: {e}")
        return False

def test_exceptions():
    """Test custom exceptions"""
    print("🧪 Testing custom exceptions...")
    
    try:
        from app.core.exceptions import (
            ValidationError, NotFoundError, AuthenticationError,
            AuthorizationError, DuplicateError, BusinessLogicError,
            create_http_exception, validation_error, not_found_error
        )
        
        # Test exception creation
        validation_exc = ValidationError("Test validation error")
        assert str(validation_exc) == "Test validation error"
        
        not_found_exc = NotFoundError("Test not found error")
        assert str(not_found_exc) == "Test not found error"
        
        # Test HTTP exception creation
        http_exc = create_http_exception(400, "Test error")
        assert http_exc.status_code == 400
        assert "Test error" in str(http_exc.detail)
        
        # Test specific error creators
        val_error = validation_error("Test validation")
        assert val_error.status_code == 422
        
        nf_error = not_found_error("User", "123")
        assert nf_error.status_code == 404
        
        print("✅ Custom exceptions work correctly!")
        return True
    except Exception as e:
        print(f"❌ Custom exceptions test failed: {e}")
        return False

def test_api_router():
    """Test API router creation"""
    print("🧪 Testing API router...")
    
    try:
        from app.api.v1.users import router
        
        assert router is not None
        assert len(router.routes) > 0
        
        # Check if expected routes exist
        route_paths = [route.path for route in router.routes]
        expected_paths = ["/", "/{user_id}", "/{user_id}/deactivate", "/{user_id}/activate"]
        
        for expected_path in expected_paths:
            assert any(expected_path in path for path in route_paths), f"Route {expected_path} not found"
        
        print("✅ API router works correctly!")
        return True
    except Exception as e:
        print(f"❌ API router test failed: {e}")
        return False

def test_middleware():
    """Test middleware creation"""
    print("🧪 Testing middleware...")
    
    try:
        from app.core.middleware import (
            RequestLoggingMiddleware, SecurityHeadersMiddleware,
            ErrorHandlingMiddleware, setup_cors_middleware,
            setup_trusted_host_middleware, setup_custom_middleware
        )
        
        # Test middleware classes can be instantiated
        logging_middleware = RequestLoggingMiddleware(None)
        security_middleware = SecurityHeadersMiddleware(None)
        error_middleware = ErrorHandlingMiddleware(None)
        
        assert logging_middleware is not None
        assert security_middleware is not None
        assert error_middleware is not None
        
        # Test setup functions exist
        assert callable(setup_cors_middleware)
        assert callable(setup_trusted_host_middleware)
        assert callable(setup_custom_middleware)
        
        print("✅ Middleware works correctly!")
        return True
    except Exception as e:
        print(f"❌ Middleware test failed: {e}")
        return False

def test_user_service_methods():
    """Test user service method signatures"""
    print("🧪 Testing user service methods...")
    
    try:
        from app.services.user_service import UserService
        from app.schemas.user import UserCreate, UserUpdate, UserFilter
        
        # Check if all expected methods exist
        expected_methods = [
            'create_user', 'get_user_by_id', 'get_user_by_email',
            'list_users', 'update_user', 'deactivate_user', 'activate_user',
            'change_password', 'get_user_stats', 'search_users',
            'get_users_by_role', 'delete_user'
        ]
        
        for method_name in expected_methods:
            assert hasattr(UserService, method_name), f"Method {method_name} not found"
            assert callable(getattr(UserService, method_name)), f"Method {method_name} is not callable"
        
        print("✅ User service methods work correctly!")
        return True
    except Exception as e:
        print(f"❌ User service methods test failed: {e}")
        return False

def test_schema_serialization():
    """Test schema serialization"""
    print("🧪 Testing schema serialization...")
    
    try:
        from app.schemas.user import UserResponse
        from datetime import datetime
        import uuid
        
        # Create a mock user response
        user_response = UserResponse(
            id=uuid.uuid4(),
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            is_active=True,
            role_id=uuid.uuid4(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Test serialization
        user_dict = user_response.dict()
        
        assert user_dict["email"] == "test@example.com"
        assert user_dict["first_name"] == "John"
        assert user_dict["last_name"] == "Doe"
        assert user_dict["is_active"] is True
        
        # Test JSON serialization
        user_json = user_response.json()
        assert "test@example.com" in user_json
        assert "John" in user_json
        
        print("✅ Schema serialization works correctly!")
        return True
    except Exception as e:
        print(f"❌ Schema serialization test failed: {e}")
        return False

def run_all_tests():
    """Run all user management tests"""
    print("🚀 Starting comprehensive user management tests...\n")
    
    tests = [
        ("Import Test", test_imports),
        ("User Schemas Test", test_user_schemas),
        ("User Service Creation Test", test_user_service_creation),
        ("User Validation Test", test_user_validation),
        ("Custom Exceptions Test", test_exceptions),
        ("API Router Test", test_api_router),
        ("Middleware Test", test_middleware),
        ("User Service Methods Test", test_user_service_methods),
        ("Schema Serialization Test", test_schema_serialization)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 ALL USER MANAGEMENT TESTS PASSED! User management is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)









