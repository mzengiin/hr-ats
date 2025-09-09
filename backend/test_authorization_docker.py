"""
Comprehensive test for authorization and security using Docker environment
"""
import os
import sys
import asyncio
from datetime import datetime
import uuid

# Add the app directory to the Python path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test that all authorization modules can be imported"""
    print("🧪 Testing authorization imports...")
    
    try:
        from app.middleware.permission_middleware import (
            PermissionMiddleware, RoleBasedMiddleware, AuditMiddleware,
            SecurityHeadersMiddleware, setup_security_middleware
        )
        from app.services.audit_service import AuditService
        from app.core.security_config import (
            setup_cors, setup_trusted_hosts, get_security_headers,
            get_rate_limit_config, get_password_policy
        )
        from app.core.validation import InputValidator, SecurityValidator
        from app.core.session_manager import SessionManager
        print("✅ All authorization modules imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_middleware_creation():
    """Test middleware creation"""
    print("🧪 Testing middleware creation...")
    
    try:
        from app.middleware.permission_middleware import (
            PermissionMiddleware, RoleBasedMiddleware, AuditMiddleware,
            SecurityHeadersMiddleware
        )
        
        # Test middleware instantiation
        permission_middleware = PermissionMiddleware(None)
        role_middleware = RoleBasedMiddleware(None)
        audit_middleware = AuditMiddleware(None)
        security_middleware = SecurityHeadersMiddleware(None)
        
        assert permission_middleware is not None
        assert role_middleware is not None
        assert audit_middleware is not None
        assert security_middleware is not None
        
        print("✅ Middleware creation works correctly!")
        return True
    except Exception as e:
        print(f"❌ Middleware creation test failed: {e}")
        return False

def test_audit_service():
    """Test audit service functionality"""
    print("🧪 Testing audit service...")
    
    try:
        from app.services.audit_service import AuditService
        from app.db.session import get_db
        
        # Get database session
        db = next(get_db())
        
        # Create audit service
        audit_service = AuditService(db)
        
        assert audit_service is not None
        assert audit_service.db == db
        
        # Test audit log creation
        audit_log = audit_service.log_event(
            user_id=uuid.uuid4(),
            action="TEST_ACTION",
            resource_type="TEST",
            details={"test": "data"}
        )
        
        assert audit_log is not None
        assert audit_log.action == "TEST_ACTION"
        assert audit_log.resource_type == "TEST"
        
        print("✅ Audit service works correctly!")
        return True
    except Exception as e:
        print(f"❌ Audit service test failed: {e}")
        return False

def test_security_config():
    """Test security configuration"""
    print("🧪 Testing security configuration...")
    
    try:
        from app.core.security_config import (
            get_security_headers, get_rate_limit_config,
            get_password_policy, get_session_config
        )
        
        # Test security headers
        headers = get_security_headers()
        assert isinstance(headers, dict)
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
        
        # Test rate limit config
        rate_config = get_rate_limit_config()
        assert isinstance(rate_config, dict)
        assert "login_attempts" in rate_config
        assert "api_requests" in rate_config
        
        # Test password policy
        password_policy = get_password_policy()
        assert isinstance(password_policy, dict)
        assert "min_length" in password_policy
        assert "require_uppercase" in password_policy
        
        # Test session config
        session_config = get_session_config()
        assert isinstance(session_config, dict)
        assert "access_token_expire_minutes" in session_config
        assert "refresh_token_expire_days" in session_config
        
        print("✅ Security configuration works correctly!")
        return True
    except Exception as e:
        print(f"❌ Security configuration test failed: {e}")
        return False

def test_input_validation():
    """Test input validation"""
    print("🧪 Testing input validation...")
    
    try:
        from app.core.validation import InputValidator, SecurityValidator
        
        # Test string sanitization
        dirty_string = "<script>alert('xss')</script>Hello World"
        clean_string = InputValidator.sanitize_string(dirty_string)
        assert "<script>" not in clean_string
        assert "Hello World" in clean_string
        
        # Test email validation
        assert InputValidator.validate_email("test@example.com") is True
        assert InputValidator.validate_email("invalid-email") is False
        
        # Test phone validation
        assert InputValidator.validate_phone("+1234567890") is True
        assert InputValidator.validate_phone("123") is False
        
        # Test password strength
        weak_password = "123"
        strong_password = "SecurePass123"
        
        weak_issues = InputValidator.validate_password_strength(weak_password)
        strong_issues = InputValidator.validate_password_strength(strong_password)
        
        assert len(weak_issues) > 0
        assert len(strong_issues) == 0
        
        # Test security validation
        assert SecurityValidator.check_sql_injection("SELECT * FROM users") is True
        assert SecurityValidator.check_sql_injection("normal text") is False
        
        assert SecurityValidator.check_xss("<script>alert('xss')</script>") is True
        assert SecurityValidator.check_xss("normal text") is False
        
        print("✅ Input validation works correctly!")
        return True
    except Exception as e:
        print(f"❌ Input validation test failed: {e}")
        return False

def test_session_management():
    """Test session management"""
    print("🧪 Testing session management...")
    
    try:
        from app.core.session_manager import SessionManager
        from app.db.session import get_db
        
        # Get database session
        db = next(get_db())
        
        # Create session manager
        session_manager = SessionManager(db)
        
        assert session_manager is not None
        assert session_manager.db == db
        
        # Test token generation
        refresh_token = session_manager._generate_refresh_token()
        assert refresh_token is not None
        assert len(refresh_token) > 0
        
        # Test token hashing
        token_hash = session_manager._hash_token(refresh_token)
        assert token_hash is not None
        assert len(token_hash) == 64  # SHA256 hash length
        
        print("✅ Session management works correctly!")
        return True
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False

def test_security_headers():
    """Test security headers"""
    print("🧪 Testing security headers...")
    
    try:
        from app.core.security_config import get_security_headers, validate_security_headers
        
        # Test getting security headers
        headers = get_security_headers()
        assert isinstance(headers, dict)
        assert len(headers) > 0
        
        # Test header validation
        issues = validate_security_headers(headers)
        assert len(issues) == 0  # Should have no issues with complete headers
        
        # Test with missing headers
        incomplete_headers = {"X-Content-Type-Options": "nosniff"}
        issues = validate_security_headers(incomplete_headers)
        assert len(issues) > 0  # Should have issues with incomplete headers
        
        print("✅ Security headers work correctly!")
        return True
    except Exception as e:
        print(f"❌ Security headers test failed: {e}")
        return False

def test_password_policy():
    """Test password policy"""
    print("🧪 Testing password policy...")
    
    try:
        from app.core.security_config import get_password_policy
        from app.core.validation import InputValidator
        
        policy = get_password_policy()
        
        # Test password validation against policy
        weak_passwords = ["123", "password", "12345678"]
        strong_passwords = ["SecurePass123", "MyP@ssw0rd!", "StrongPwd2024"]
        
        for weak_pwd in weak_passwords:
            issues = InputValidator.validate_password_strength(weak_pwd)
            assert len(issues) > 0, f"Weak password {weak_pwd} should have issues"
        
        for strong_pwd in strong_passwords:
            issues = InputValidator.validate_password_strength(strong_pwd)
            assert len(issues) == 0, f"Strong password {strong_pwd} should have no issues"
        
        print("✅ Password policy works correctly!")
        return True
    except Exception as e:
        print(f"❌ Password policy test failed: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting configuration"""
    print("🧪 Testing rate limiting...")
    
    try:
        from app.core.security_config import get_rate_limit_config
        
        config = get_rate_limit_config()
        
        # Test login attempts config
        login_config = config["login_attempts"]
        assert "max_attempts" in login_config
        assert "lockout_duration" in login_config
        assert "window_duration" in login_config
        
        # Test API requests config
        api_config = config["api_requests"]
        assert "max_requests" in api_config
        assert "window_duration" in api_config
        
        # Test password reset config
        reset_config = config["password_reset"]
        assert "max_attempts" in reset_config
        assert "lockout_duration" in reset_config
        
        print("✅ Rate limiting works correctly!")
        return True
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False

def test_security_compliance():
    """Test security compliance check"""
    print("🧪 Testing security compliance...")
    
    try:
        from app.core.security_config import check_security_compliance
        
        compliance = check_security_compliance()
        
        assert isinstance(compliance, dict)
        assert "overall_score" in compliance
        assert "https_enabled" in compliance
        assert "cors_configured" in compliance
        assert "rate_limiting_enabled" in compliance
        assert "audit_logging_enabled" in compliance
        
        # Overall score should be between 0 and 100
        assert 0 <= compliance["overall_score"] <= 100
        
        print("✅ Security compliance works correctly!")
        return True
    except Exception as e:
        print(f"❌ Security compliance test failed: {e}")
        return False

def run_all_tests():
    """Run all authorization and security tests"""
    print("🚀 Starting comprehensive authorization and security tests...\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Middleware Creation Test", test_middleware_creation),
        ("Audit Service Test", test_audit_service),
        ("Security Configuration Test", test_security_config),
        ("Input Validation Test", test_input_validation),
        ("Session Management Test", test_session_management),
        ("Security Headers Test", test_security_headers),
        ("Password Policy Test", test_password_policy),
        ("Rate Limiting Test", test_rate_limiting),
        ("Security Compliance Test", test_security_compliance)
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
        print("🎉 ALL AUTHORIZATION AND SECURITY TESTS PASSED! Security is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)









