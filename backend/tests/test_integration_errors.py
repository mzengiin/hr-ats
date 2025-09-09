"""
Integration tests for error scenarios and edge cases
"""
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.user_role import UserRole
from app.core.security import get_password_hash

# Test data
TEST_USER_DATA = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "password": "testpassword123"
}

class TestErrorScenarios:
    """Error scenarios and edge cases integration tests"""
    
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
    
    async def test_invalid_json_requests(self, client: AsyncClient):
        """Test handling of invalid JSON requests"""
        # Test malformed JSON
        response = await client.post(
            "/api/v1/auth/login",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # Test empty JSON
        response = await client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422
        
        # Test missing required fields
        response = await client.post("/api/v1/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422
        
        response = await client.post("/api/v1/auth/login", json={"password": "password123"})
        assert response.status_code == 422
    
    async def test_validation_errors(self, client: AsyncClient):
        """Test input validation errors"""
        # Test invalid email format
        response = await client.post("/api/v1/auth/login", json={
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422
        
        # Test empty strings
        response = await client.post("/api/v1/auth/login", json={
            "email": "",
            "password": ""
        })
        assert response.status_code == 422
        
        # Test too long strings
        long_string = "a" * 1000
        response = await client.post("/api/v1/auth/login", json={
            "email": f"{long_string}@example.com",
            "password": "password123"
        })
        assert response.status_code == 422
        
        # Test special characters in email
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com<script>alert('xss')</script>",
            "password": "password123"
        })
        assert response.status_code == 422
    
    async def test_authentication_errors(self, client: AsyncClient, test_user: User):
        """Test authentication error scenarios"""
        # Test wrong password
        response = await client.post("/api/v1/auth/login", json={
            "email": TEST_USER_DATA["email"],
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        
        # Test non-existent user
        response = await client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        assert response.status_code == 401
        
        # Test inactive user
        test_user.is_active = False
        db_session = test_user.__dict__['_sa_instance_state'].session
        db_session.commit()
        
        response = await client.post("/api/v1/auth/login", json=TEST_USER_DATA)
        assert response.status_code == 401
        
        # Test with empty credentials
        response = await client.post("/api/v1/auth/login", json={
            "email": "",
            "password": ""
        })
        assert response.status_code == 422
    
    async def test_authorization_errors(self, client: AsyncClient, test_user: User):
        """Test authorization error scenarios"""
        # Test accessing protected endpoint without token
        response = await client.get("/api/v1/users/")
        assert response.status_code == 401
        
        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 401
        
        # Test with malformed Authorization header
        headers = {"Authorization": "InvalidFormat token"}
        response = await client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 401
        
        # Test with expired token (simulated)
        headers = {"Authorization": "Bearer expired_token"}
        response = await client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 401
    
    async def test_rate_limiting_errors(self, client: AsyncClient, test_user: User):
        """Test rate limiting error scenarios"""
        # Test rate limiting on login attempts
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": "wrongpassword"
        }
        
        # Make multiple failed attempts
        for i in range(10):
            response = await client.post("/api/v1/auth/login", json=login_data)
            if response.status_code == 429:
                break
        
        # Should eventually hit rate limit
        assert response.status_code == 429
        
        # Test rate limiting on registration
        registration_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "new@example.com",
            "password": "password123"
        }
        
        # Make multiple registration attempts
        for i in range(10):
            response = await client.post("/api/v1/auth/register", json=registration_data)
            if response.status_code == 429:
                break
        
        # Should eventually hit rate limit
        assert response.status_code == 429
    
    async def test_database_errors(self, client: AsyncClient, db_session: Session):
        """Test database error scenarios"""
        # Test duplicate email registration
        # First registration
        response = await client.post("/api/v1/auth/register", json=TEST_USER_DATA)
        assert response.status_code == 201
        
        # Second registration with same email
        response = await client.post("/api/v1/auth/register", json=TEST_USER_DATA)
        assert response.status_code == 409  # Conflict
        
        # Test invalid role ID
        response = await client.post("/api/v1/users/", json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test2@example.com",
            "password": "password123",
            "role_id": "invalid-role-id"
        })
        assert response.status_code == 400
    
    async def test_concurrent_error_scenarios(self, client: AsyncClient, test_user: User):
        """Test concurrent error scenarios"""
        # Test concurrent failed login attempts
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": "wrongpassword"
        }
        
        # Create multiple concurrent failed login attempts
        tasks = []
        for i in range(20):
            task = client.post("/api/v1/auth/login", json=login_data)
            tasks.append(task)
        
        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all requests failed
        failed_responses = [r for r in responses if not isinstance(r, Exception) and r.status_code in [401, 429]]
        assert len(failed_responses) == 20
        
        # Test concurrent registration with same email
        registration_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "concurrent@example.com",
            "password": "password123"
        }
        
        # Create multiple concurrent registration attempts
        tasks = []
        for i in range(10):
            task = client.post("/api/v1/auth/register", json=registration_data)
            tasks.append(task)
        
        # Execute all requests concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify only one succeeded, others failed
        successful_responses = [r for r in responses if not isinstance(r, Exception) and r.status_code == 201]
        failed_responses = [r for r in responses if not isinstance(r, Exception) and r.status_code == 409]
        
        assert len(successful_responses) == 1
        assert len(failed_responses) == 9
    
    async def test_malicious_input_handling(self, client: AsyncClient):
        """Test handling of malicious input"""
        # Test SQL injection attempts
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "'; INSERT INTO users VALUES ('hacker', 'hacker@evil.com', 'password'); --"
        ]
        
        for malicious_input in malicious_inputs:
            response = await client.post("/api/v1/auth/login", json={
                "email": malicious_input,
                "password": "password123"
            })
            # Should not crash, should return validation error or 401
            assert response.status_code in [401, 422]
        
        # Test XSS attempts
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for xss_input in xss_inputs:
            response = await client.post("/api/v1/auth/login", json={
                "email": f"{xss_input}@example.com",
                "password": "password123"
            })
            # Should not crash, should return validation error
            assert response.status_code in [401, 422]
    
    async def test_large_payload_handling(self, client: AsyncClient):
        """Test handling of large payloads"""
        # Test very large email
        large_email = "a" * 1000 + "@example.com"
        response = await client.post("/api/v1/auth/login", json={
            "email": large_email,
            "password": "password123"
        })
        assert response.status_code == 422
        
        # Test very large password
        large_password = "a" * 1000
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": large_password
        })
        assert response.status_code == 422
        
        # Test very large JSON payload
        large_data = {
            "first_name": "a" * 1000,
            "last_name": "a" * 1000,
            "email": "test@example.com",
            "password": "password123"
        }
        response = await client.post("/api/v1/auth/register", json=large_data)
        assert response.status_code == 422
    
    async def test_network_error_simulation(self, client: AsyncClient):
        """Test network error simulation"""
        # Test with invalid endpoint
        response = await client.get("/api/v1/invalid-endpoint")
        assert response.status_code == 404
        
        # Test with invalid HTTP method
        response = await client.patch("/api/v1/auth/login")
        assert response.status_code == 405
        
        # Test with missing Content-Type header
        response = await client.post(
            "/api/v1/auth/login",
            content='{"email": "test@example.com", "password": "password123"}'
        )
        # Should still work as JSON is auto-detected
        assert response.status_code in [200, 401, 422]
    
    async def test_edge_case_data_types(self, client: AsyncClient):
        """Test edge case data types"""
        # Test with null values
        response = await client.post("/api/v1/auth/login", json={
            "email": None,
            "password": None
        })
        assert response.status_code == 422
        
        # Test with numeric values
        response = await client.post("/api/v1/auth/login", json={
            "email": 123,
            "password": 456
        })
        assert response.status_code == 422
        
        # Test with boolean values
        response = await client.post("/api/v1/auth/login", json={
            "email": True,
            "password": False
        })
        assert response.status_code == 422
        
        # Test with array values
        response = await client.post("/api/v1/auth/login", json={
            "email": ["test@example.com"],
            "password": ["password123"]
        })
        assert response.status_code == 422
    
    async def test_timeout_scenarios(self, client: AsyncClient, test_user: User):
        """Test timeout scenarios"""
        # Test with very slow request (simulated)
        # This would require mocking the database to be slow
        # For now, just test that the endpoint responds
        response = await client.get("/api/v1/users/")
        assert response.status_code == 401  # Unauthorized, but not timeout
        
        # Test with valid request
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": TEST_USER_DATA["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
    
    async def test_memory_limit_scenarios(self, client: AsyncClient):
        """Test memory limit scenarios"""
        # Test with very large number of users request
        response = await client.get("/api/v1/users/?limit=1000000")
        # Should be limited by pagination
        assert response.status_code == 401  # Unauthorized, but not memory error
        
        # Test with very large search term
        response = await client.get("/api/v1/users/?search=" + "a" * 10000)
        assert response.status_code == 401  # Unauthorized, but not memory error









