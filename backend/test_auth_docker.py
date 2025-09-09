"""
Comprehensive test for authentication core using Docker environment
"""
import os
import sys
import asyncio
from datetime import datetime, timedelta
import uuid

# Add the app directory to the Python path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test that all authentication modules can be imported"""
    print("🧪 Testing authentication imports...")
    
    try:
        from app.core.security import (
            create_access_token,
            create_refresh_token,
            verify_token,
            get_password_hash,
            verify_password,
            TokenData
        )
        from app.services.token_service import TokenService
        from app.core.auth import get_current_user, require_role, require_permission
        from app.core.rate_limiter import RateLimiter, check_rate_limit
        print("✅ All authentication modules imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_password_hashing():
    """Test password hashing functionality"""
    print("🧪 Testing password hashing...")
    
    try:
        from app.core.security import get_password_hash, verify_password
        
        # Test password hashing
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        assert len(hashed) > 0
        
        # Should be able to verify correct password
        assert verify_password(password, hashed) is True
        
        # Should reject incorrect password
        assert verify_password("wrong_password", hashed) is False
        
        print("✅ Password hashing works correctly!")
        return True
    except Exception as e:
        print(f"❌ Password hashing test failed: {e}")
        return False

def test_jwt_tokens():
    """Test JWT token creation and verification"""
    print("🧪 Testing JWT tokens...")
    
    try:
        from app.core.security import create_access_token, create_refresh_token, verify_token
        
        user_id = str(uuid.uuid4())
        
        # Test access token creation
        access_token = create_access_token(data={"sub": user_id})
        assert access_token is not None
        assert isinstance(access_token, str)
        assert len(access_token) > 0
        
        # Test refresh token creation
        refresh_token = create_refresh_token(data={"sub": user_id})
        assert refresh_token is not None
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0
        
        # Test token verification
        access_data = verify_token(access_token)
        assert access_data.sub == user_id
        
        refresh_data = verify_token(refresh_token)
        assert refresh_data.sub == user_id
        
        print("✅ JWT tokens work correctly!")
        return True
    except Exception as e:
        print(f"❌ JWT token test failed: {e}")
        return False

def test_token_data():
    """Test TokenData model"""
    print("🧪 Testing TokenData model...")
    
    try:
        from app.core.security import TokenData
        
        user_id = str(uuid.uuid4())
        token_data = TokenData(sub=user_id)
        
        assert token_data.sub == user_id
        assert token_data.exp is None
        
        # Test with expiration
        exp_time = datetime.utcnow() + timedelta(minutes=15)
        token_data_with_exp = TokenData(sub=user_id, exp=exp_time)
        
        assert token_data_with_exp.sub == user_id
        assert token_data_with_exp.exp == exp_time
        
        print("✅ TokenData model works correctly!")
        return True
    except Exception as e:
        print(f"❌ TokenData test failed: {e}")
        return False

def test_rate_limiter():
    """Test rate limiting functionality"""
    print("🧪 Testing rate limiter...")
    
    try:
        from app.core.rate_limiter import RateLimiter
        
        # Create rate limiter
        limiter = RateLimiter()
        
        # Test normal operation
        key = "test_key"
        
        # Should allow requests under limit
        for i in range(5):  # Default limit is 5 per minute
            assert limiter.is_allowed(key) is True
        
        # Should block requests over limit
        assert limiter.is_allowed(key) is False
        
        # Test reset
        limiter.reset(key)
        assert limiter.is_allowed(key) is True
        
        print("✅ Rate limiter works correctly!")
        return True
    except Exception as e:
        print(f"❌ Rate limiter test failed: {e}")
        return False

def test_login_tracker():
    """Test login attempt tracking"""
    print("🧪 Testing login tracker...")
    
    try:
        from app.core.rate_limiter import LoginAttemptTracker
        
        tracker = LoginAttemptTracker()
        email = "test@example.com"
        
        # Test failed attempts
        for i in range(4):
            tracker.record_failed_attempt(email)
            assert tracker.is_locked_out(email) is False
        
        # 5th failed attempt should lock out
        tracker.record_failed_attempt(email)
        assert tracker.is_locked_out(email) is True
        
        # Test successful attempt clears lockout
        tracker.record_successful_attempt(email)
        assert tracker.is_locked_out(email) is False
        
        print("✅ Login tracker works correctly!")
        return True
    except Exception as e:
        print(f"❌ Login tracker test failed: {e}")
        return False

def test_security_integration():
    """Test complete security workflow"""
    print("🧪 Testing security integration...")
    
    try:
        from app.core.security import (
            get_password_hash,
            verify_password,
            create_access_token,
            create_refresh_token,
            verify_token
        )
        
        # 1. Hash password
        password = "secure_password_123"
        hashed_password = get_password_hash(password)
        
        # 2. Verify password
        assert verify_password(password, hashed_password) is True
        
        # 3. Create tokens for user
        user_id = str(uuid.uuid4())
        access_token = create_access_token(data={"sub": user_id})
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        # 4. Verify tokens
        access_data = verify_token(access_token)
        refresh_data = verify_token(refresh_token)
        
        assert access_data.sub == user_id
        assert refresh_data.sub == user_id
        
        print("✅ Security integration works correctly!")
        return True
    except Exception as e:
        print(f"❌ Security integration test failed: {e}")
        return False

def run_all_tests():
    """Run all authentication tests"""
    print("🚀 Starting comprehensive authentication tests...\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Password Hashing Test", test_password_hashing),
        ("JWT Tokens Test", test_jwt_tokens),
        ("TokenData Test", test_token_data),
        ("Rate Limiter Test", test_rate_limiter),
        ("Login Tracker Test", test_login_tracker),
        ("Security Integration Test", test_security_integration)
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
        print("🎉 ALL AUTHENTICATION TESTS PASSED! Core auth is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)









