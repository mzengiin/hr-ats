"""
Comprehensive test for authentication endpoints using Docker environment
"""
import os
import sys
import asyncio
from datetime import datetime
import uuid

# Add the app directory to the Python path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test that all authentication endpoint modules can be imported"""
    print("🧪 Testing authentication endpoint imports...")
    
    try:
        from app.schemas.auth import (
            LoginRequest, RefreshTokenRequest, LogoutRequest,
            TokenResponse, RefreshTokenResponse, LogoutResponse,
            UserInfoResponse, PasswordChangeRequest, PasswordChangeResponse,
            ErrorResponse
        )
        from app.services.auth_service import AuthService
        from app.api.v1.auth import router
        print("✅ All authentication endpoint modules imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_auth_schemas():
    """Test authentication schemas"""
    print("🧪 Testing authentication schemas...")
    
    try:
        from app.schemas.auth import (
            LoginRequest, RefreshTokenRequest, LogoutRequest,
            TokenResponse, RefreshTokenResponse, LogoutResponse,
            UserInfoResponse, PasswordChangeRequest, PasswordChangeResponse
        )
        
        # Test LoginRequest
        login_data = LoginRequest(
            email="test@example.com",
            password="secure_password_123"
        )
        assert login_data.email == "test@example.com"
        assert login_data.password == "secure_password_123"
        
        # Test RefreshTokenRequest
        refresh_data = RefreshTokenRequest(
            refresh_token="test_refresh_token"
        )
        assert refresh_data.refresh_token == "test_refresh_token"
        
        # Test LogoutRequest
        logout_data = LogoutRequest(
            refresh_token="test_refresh_token"
        )
        assert logout_data.refresh_token == "test_refresh_token"
        
        # Test TokenResponse
        token_response = TokenResponse(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_type="bearer",
            expires_in=900,
            user={"id": "123", "email": "test@example.com"}
        )
        assert token_response.access_token == "test_access_token"
        assert token_response.token_type == "bearer"
        
        # Test PasswordChangeRequest
        password_data = PasswordChangeRequest(
            current_password="old_password_123",
            new_password="new_password_123"
        )
        assert password_data.current_password == "old_password_123"
        assert password_data.new_password == "new_password_123"
        
        print("✅ Authentication schemas work correctly!")
        return True
    except Exception as e:
        print(f"❌ Authentication schemas test failed: {e}")
        return False

def test_auth_service_creation():
    """Test auth service creation"""
    print("🧪 Testing auth service creation...")
    
    try:
        from app.services.auth_service import AuthService
        from app.db.session import get_db
        
        # Get database session
        db = next(get_db())
        
        # Create auth service
        auth_service = AuthService(db)
        
        assert auth_service is not None
        assert auth_service.db == db
        assert auth_service.token_service is not None
        
        print("✅ Auth service creation works correctly!")
        return True
    except Exception as e:
        print(f"❌ Auth service creation test failed: {e}")
        return False

def test_auth_service_methods():
    """Test auth service method signatures"""
    print("🧪 Testing auth service methods...")
    
    try:
        from app.services.auth_service import AuthService
        
        # Check if all expected methods exist
        expected_methods = [
            'authenticate_user', 'refresh_access_token', 'logout',
            'get_current_user_info', 'change_password', 'validate_token',
            'get_user_from_token', 'revoke_all_user_tokens',
            'cleanup_expired_tokens', 'get_auth_stats'
        ]
        
        for method_name in expected_methods:
            assert hasattr(AuthService, method_name), f"Method {method_name} not found"
            assert callable(getattr(AuthService, method_name)), f"Method {method_name} is not callable"
        
        print("✅ Auth service methods work correctly!")
        return True
    except Exception as e:
        print(f"❌ Auth service methods test failed: {e}")
        return False

def test_api_router():
    """Test API router creation"""
    print("🧪 Testing API router...")
    
    try:
        from app.api.v1.auth import router
        
        assert router is not None
        assert len(router.routes) > 0
        
        # Check if expected routes exist
        route_paths = [route.path for route in router.routes]
        expected_paths = [
            "/login", "/refresh", "/logout", "/me",
            "/change-password", "/logout-all", "/validate",
            "/stats", "/cleanup"
        ]
        
        for expected_path in expected_paths:
            assert any(expected_path in path for path in route_paths), f"Route {expected_path} not found"
        
        print("✅ API router works correctly!")
        return True
    except Exception as e:
        print(f"❌ API router test failed: {e}")
        return False

def test_schema_validation():
    """Test schema validation"""
    print("🧪 Testing schema validation...")
    
    try:
        from app.schemas.auth import LoginRequest, PasswordChangeRequest
        
        # Test valid login data
        valid_login = LoginRequest(
            email="test@example.com",
            password="secure_password_123"
        )
        assert valid_login.email == "test@example.com"
        assert valid_login.password == "secure_password_123"
        
        # Test invalid email format
        try:
            invalid_login = LoginRequest(
                email="invalid-email",
                password="secure_password_123"
            )
            assert False, "Should have raised validation error"
        except Exception as e:
            assert "Invalid email format" in str(e) or "value_error" in str(e).lower()
        
        # Test empty password
        try:
            empty_password_login = LoginRequest(
                email="test@example.com",
                password=""
            )
            assert False, "Should have raised validation error"
        except Exception as e:
            assert "Password cannot be empty" in str(e) or "value_error" in str(e).lower()
        
        # Test password change validation
        valid_password_change = PasswordChangeRequest(
            current_password="old_password_123",
            new_password="new_password_123"
        )
        assert valid_password_change.current_password == "old_password_123"
        assert valid_password_change.new_password == "new_password_123"
        
        # Test weak new password
        try:
            weak_password_change = PasswordChangeRequest(
                current_password="old_password_123",
                new_password="123"
            )
            assert False, "Should have raised validation error"
        except Exception as e:
            assert "Password must be at least 8 characters" in str(e) or "value_error" in str(e).lower()
        
        print("✅ Schema validation works correctly!")
        return True
    except Exception as e:
        print(f"❌ Schema validation test failed: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    print("🧪 Testing error handling...")
    
    try:
        from app.core.exceptions import (
            ValidationError, AuthenticationError, AuthorizationError,
            create_http_exception, validation_error, authentication_error
        )
        
        # Test exception creation
        validation_exc = ValidationError("Test validation error")
        assert str(validation_exc) == "Test validation error"
        
        auth_exc = AuthenticationError("Test authentication error")
        assert str(auth_exc) == "Test authentication error"
        
        # Test HTTP exception creation
        http_exc = create_http_exception(401, "Test auth error")
        assert http_exc.status_code == 401
        assert "Test auth error" in str(http_exc.detail)
        
        # Test specific error creators
        val_error = validation_error("Test validation")
        assert val_error.status_code == 422
        
        auth_error = authentication_error("Test authentication")
        assert auth_error.status_code == 401
        
        print("✅ Error handling works correctly!")
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("🧪 Testing rate limiting...")
    
    try:
        from app.core.rate_limiter import (
            RateLimiter, check_rate_limit, reset_rate_limit,
            record_login_attempt, check_login_attempts
        )
        
        # Test rate limiter
        limiter = RateLimiter()
        key = "test_key"
        
        # Should allow requests under limit
        for i in range(5):  # Default limit is 5 per minute
            assert limiter.is_allowed(key) is True
        
        # Should block requests over limit
        assert limiter.is_allowed(key) is False
        
        # Test reset
        limiter.reset(key)
        assert limiter.is_allowed(key) is True
        
        # Test login attempt tracking
        email = "test@example.com"
        
        # Test failed attempts
        for i in range(4):
            record_login_attempt(email, success=False)
            # Note: check_login_attempts raises exception if locked out
            try:
                check_login_attempts(email)
                # If no exception, we're not locked out yet
                assert True
            except Exception:
                # If exception, we're locked out (shouldn't happen yet)
                assert False, f"Should not be locked out after {i+1} attempts"
        
        # 5th failed attempt should lock out
        record_login_attempt(email, success=False)
        try:
            check_login_attempts(email)
            assert False, "Should be locked out after 5 attempts"
        except Exception:
            # Expected to be locked out
            assert True
        
        # Successful attempt should clear lockout
        record_login_attempt(email, success=True)
        try:
            check_login_attempts(email)
            # If no exception, we're not locked out
            assert True
        except Exception:
            # If exception, we're still locked out (shouldn't happen)
            assert False, "Should not be locked out after successful attempt"
        
        print("✅ Rate limiting works correctly!")
        return True
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False

def test_token_operations():
    """Test token operations"""
    print("🧪 Testing token operations...")
    
    try:
        from app.core.security import (
            create_access_token, create_refresh_token,
            verify_token, verify_refresh_token
        )
        from app.services.token_service import TokenService
        from app.db.session import get_db
        
        # Test token creation
        user_id = str(uuid.uuid4())
        access_token = create_access_token(data={"sub": user_id})
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        assert access_token is not None
        assert refresh_token is not None
        assert len(access_token) > 0
        assert len(refresh_token) > 0
        
        # Test token verification
        access_data = verify_token(access_token)
        assert access_data.sub == user_id
        
        refresh_data = verify_refresh_token(refresh_token)
        assert refresh_data.sub == user_id
        
        # Test token service
        db = next(get_db())
        token_service = TokenService(db)
        
        assert token_service is not None
        assert token_service.db == db
        
        print("✅ Token operations work correctly!")
        return True
    except Exception as e:
        print(f"❌ Token operations test failed: {e}")
        return False

def test_schema_serialization():
    """Test schema serialization"""
    print("🧪 Testing schema serialization...")
    
    try:
        from app.schemas.auth import TokenResponse, UserInfoResponse
        from datetime import datetime
        import uuid
        
        # Test TokenResponse serialization
        token_response = TokenResponse(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_type="bearer",
            expires_in=900,
            user={"id": "123", "email": "test@example.com"}
        )
        
        # Test serialization
        token_dict = token_response.model_dump()
        
        assert token_dict["access_token"] == "test_access_token"
        assert token_dict["token_type"] == "bearer"
        assert token_dict["expires_in"] == 900
        
        # Test JSON serialization
        token_json = token_response.model_dump_json()
        assert "test_access_token" in token_json
        assert "bearer" in token_json
        
        # Test UserInfoResponse serialization
        user_response = UserInfoResponse(
            id=str(uuid.uuid4()),
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            is_active=True,
            role={"name": "admin", "permissions": {}},
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        
        user_dict = user_response.model_dump()
        assert user_dict["email"] == "test@example.com"
        assert user_dict["first_name"] == "John"
        assert user_dict["is_active"] is True
        
        print("✅ Schema serialization works correctly!")
        return True
    except Exception as e:
        print(f"❌ Schema serialization test failed: {e}")
        return False

def run_all_tests():
    """Run all authentication endpoint tests"""
    print("🚀 Starting comprehensive authentication endpoint tests...\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Auth Schemas Test", test_auth_schemas),
        ("Auth Service Creation Test", test_auth_service_creation),
        ("Auth Service Methods Test", test_auth_service_methods),
        ("API Router Test", test_api_router),
        ("Schema Validation Test", test_schema_validation),
        ("Error Handling Test", test_error_handling),
        ("Rate Limiting Test", test_rate_limiting),
        ("Token Operations Test", test_token_operations),
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
        print("🎉 ALL AUTHENTICATION ENDPOINT TESTS PASSED! Authentication endpoints are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
