"""
Comprehensive test for database models using Docker environment
"""
import os
import sys
import asyncio
from datetime import datetime, timedelta
import uuid

# Add the app directory to the Python path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test that all models can be imported"""
    print("🧪 Testing model imports...")
    
    try:
        from app.models.user import User
        from app.models.user_role import UserRole
        from app.models.refresh_token import RefreshToken
        from app.models.audit_log import AuditLog
        from app.db.base import Base
        print("✅ All models imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_model_creation():
    """Test model creation without database"""
    print("🧪 Testing model creation...")
    
    try:
        from app.models.user_role import UserRole
        from app.models.user import User
        from app.models.refresh_token import RefreshToken
        from app.models.audit_log import AuditLog
        
        # Test UserRole creation
        role = UserRole(
            name="test_role",
            description="Test Role",
            permissions={"test": ["read", "write"]}
        )
        print(f"✅ UserRole created: {role.name}")
        
        # Test User creation
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            role_id=uuid.uuid4()
        )
        print(f"✅ User created: {user.email}")
        
        # Test RefreshToken creation
        token = RefreshToken(
            user_id=user.id,
            token_hash="hashed_token",
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        print(f"✅ RefreshToken created: {token.id}")
        
        # Test AuditLog creation
        audit_log = AuditLog(
            user_id=user.id,
            action="test_action",
            resource="test_resource",
            ip_address="192.168.1.1",
            user_agent="Test Agent"
        )
        print(f"✅ AuditLog created: {audit_log.id}")
        
        return True
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def test_model_relationships():
    """Test model relationships"""
    print("🧪 Testing model relationships...")
    
    try:
        from app.models.user import User
        from app.models.user_role import UserRole
        from app.models.refresh_token import RefreshToken
        from app.models.audit_log import AuditLog
        
        # Create role
        role = UserRole(
            name="hr_manager",
            description="HR Manager",
            permissions={"candidates": ["read", "create", "update"]}
        )
        
        # Create user with role
        user = User(
            email="manager@example.com",
            password_hash="hashed_password",
            first_name="Manager",
            last_name="User",
            role_id=role.id
        )
        
        # Test full_name property
        assert user.full_name == "Manager User"
        print(f"✅ User full_name property: {user.full_name}")
        
        # Test token expiration
        token = RefreshToken(
            user_id=user.id,
            token_hash="hashed_token",
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        # Test is_expired property
        assert not token.is_expired
        print(f"✅ Token expiration check: {not token.is_expired}")
        
        return True
    except Exception as e:
        print(f"❌ Relationship test failed: {e}")
        return False

def test_database_metadata():
    """Test database metadata"""
    print("🧪 Testing database metadata...")
    
    try:
        from app.db.base import Base
        
        # Check that all tables are registered
        tables = list(Base.metadata.tables.keys())
        expected_tables = ['users', 'user_roles', 'refresh_tokens', 'audit_logs']
        
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in metadata"
            print(f"✅ Table {table} found in metadata")
        
        print(f"✅ All {len(tables)} tables registered in metadata")
        return True
    except Exception as e:
        print(f"❌ Metadata test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting comprehensive model tests...\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Model Creation Test", test_model_creation),
        ("Relationship Test", test_model_relationships),
        ("Metadata Test", test_database_metadata)
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
        print("🎉 ALL TESTS PASSED! Models are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)









