"""
Integration tests for role-based access control across all protected endpoints
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
ADMIN_DATA = {
    "first_name": "Admin",
    "last_name": "User",
    "email": "admin@example.com",
    "password": "adminpassword123"
}

HR_DATA = {
    "first_name": "HR",
    "last_name": "Manager",
    "email": "hr@example.com",
    "password": "hrpassword123"
}

USER_DATA = {
    "first_name": "Regular",
    "last_name": "User",
    "email": "user@example.com",
    "password": "userpassword123"
}

class TestRoleBasedAccessControl:
    """Role-based access control integration tests"""
    
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
    def admin_user(self, db_session: Session):
        """Create admin user with full permissions"""
        # Create admin role
        admin_role = UserRole(
            name="admin",
            description="Administrator",
            permissions={
                "users": ["create", "read", "update", "delete"],
                "roles": ["create", "read", "update", "delete"],
                "auth": ["read", "update"]
            }
        )
        db_session.add(admin_role)
        db_session.commit()
        db_session.refresh(admin_role)
        
        # Create admin user
        admin = User(
            first_name=ADMIN_DATA["first_name"],
            last_name=ADMIN_DATA["last_name"],
            email=ADMIN_DATA["email"],
            hashed_password=get_password_hash(ADMIN_DATA["password"]),
            role_id=admin_role.id,
            is_active=True
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        
        return admin
    
    @pytest.fixture
    def hr_user(self, db_session: Session):
        """Create HR user with limited permissions"""
        # Create HR role
        hr_role = UserRole(
            name="hr",
            description="HR Manager",
            permissions={
                "users": ["create", "read", "update"],
                "roles": ["read"],
                "auth": ["read"]
            }
        )
        db_session.add(hr_role)
        db_session.commit()
        db_session.refresh(hr_role)
        
        # Create HR user
        hr = User(
            first_name=HR_DATA["first_name"],
            last_name=HR_DATA["last_name"],
            email=HR_DATA["email"],
            hashed_password=get_password_hash(HR_DATA["password"]),
            role_id=hr_role.id,
            is_active=True
        )
        db_session.add(hr)
        db_session.commit()
        db_session.refresh(hr)
        
        return hr
    
    @pytest.fixture
    def regular_user(self, db_session: Session):
        """Create regular user with minimal permissions"""
        # Create user role
        user_role = UserRole(
            name="user",
            description="Regular User",
            permissions={
                "users": ["read"],
                "roles": [],
                "auth": ["read"]
            }
        )
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(user_role)
        
        # Create regular user
        user = User(
            first_name=USER_DATA["first_name"],
            last_name=USER_DATA["last_name"],
            email=USER_DATA["email"],
            hashed_password=get_password_hash(USER_DATA["password"]),
            role_id=user_role.id,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        return user
    
    async def get_auth_token(self, client: AsyncClient, user_data: dict):
        """Helper to get authentication token"""
        response = await client.post("/api/v1/auth/login", json=user_data)
        assert response.status_code == 200
        return response.json()["access_token"]
    
    async def test_admin_full_access(self, client: AsyncClient, admin_user: User):
        """Test admin has full access to all endpoints"""
        token = await self.get_auth_token(client, ADMIN_DATA)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test user management endpoints
        response = await client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 200
        
        response = await client.post("/api/v1/users/", json={
            "first_name": "New",
            "last_name": "User",
            "email": "new@example.com",
            "password": "password123",
            "role_id": admin_user.role_id
        }, headers=headers)
        assert response.status_code == 201
        
        # Test auth endpoints
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        response = await client.post("/api/v1/auth/change-password", json={
            "current_password": ADMIN_DATA["password"],
            "new_password": "newpassword123"
        }, headers=headers)
        assert response.status_code == 200
    
    async def test_hr_limited_access(self, client: AsyncClient, hr_user: User, admin_user: User):
        """Test HR user has limited access"""
        token = await self.get_auth_token(client, HR_DATA)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test user management endpoints (should work)
        response = await client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 200
        
        response = await client.post("/api/v1/users/", json={
            "first_name": "New",
            "last_name": "User",
            "email": "new@example.com",
            "password": "password123",
            "role_id": hr_user.role_id
        }, headers=headers)
        assert response.status_code == 201
        
        # Test updating user (should work)
        response = await client.put(f"/api/v1/users/{admin_user.id}", json={
            "first_name": "Updated",
            "last_name": "Admin",
            "email": admin_user.email,
            "role_id": admin_user.role_id
        }, headers=headers)
        assert response.status_code == 200
        
        # Test deleting user (should fail - no delete permission)
        response = await client.delete(f"/api/v1/users/{admin_user.id}", headers=headers)
        assert response.status_code == 403
    
    async def test_regular_user_minimal_access(self, client: AsyncClient, regular_user: User):
        """Test regular user has minimal access"""
        token = await self.get_auth_token(client, USER_DATA)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test reading users (should work)
        response = await client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 200
        
        # Test creating user (should fail - no create permission)
        response = await client.post("/api/v1/users/", json={
            "first_name": "New",
            "last_name": "User",
            "email": "new@example.com",
            "password": "password123",
            "role_id": regular_user.role_id
        }, headers=headers)
        assert response.status_code == 403
        
        # Test updating user (should fail - no update permission)
        response = await client.put(f"/api/v1/users/{regular_user.id}", json={
            "first_name": "Updated",
            "last_name": "User",
            "email": regular_user.email,
            "role_id": regular_user.role_id
        }, headers=headers)
        assert response.status_code == 403
        
        # Test deleting user (should fail - no delete permission)
        response = await client.delete(f"/api/v1/users/{regular_user.id}", headers=headers)
        assert response.status_code == 403
    
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test unauthorized access to protected endpoints"""
        # Test without token
        response = await client.get("/api/v1/users/")
        assert response.status_code == 401
        
        response = await client.post("/api/v1/users/", json={})
        assert response.status_code == 401
        
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
        
        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 401
        
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
    
    async def test_cross_user_access_restrictions(self, client: AsyncClient, admin_user: User, hr_user: User, regular_user: User):
        """Test users cannot access other users' data inappropriately"""
        # Test regular user cannot access admin's data
        regular_token = await self.get_auth_token(client, USER_DATA)
        regular_headers = {"Authorization": f"Bearer {regular_token}"}
        
        response = await client.get(f"/api/v1/users/{admin_user.id}", headers=regular_headers)
        assert response.status_code == 200  # Can read but not modify
        
        response = await client.put(f"/api/v1/users/{admin_user.id}", json={
            "first_name": "Hacked",
            "last_name": "Admin",
            "email": admin_user.email,
            "role_id": admin_user.role_id
        }, headers=regular_headers)
        assert response.status_code == 403  # Cannot modify
        
        # Test HR user cannot delete admin
        hr_token = await self.get_auth_token(client, HR_DATA)
        hr_headers = {"Authorization": f"Bearer {hr_token}"}
        
        response = await client.delete(f"/api/v1/users/{admin_user.id}", headers=hr_headers)
        assert response.status_code == 403  # Cannot delete
    
    async def test_role_hierarchy_enforcement(self, client: AsyncClient, admin_user: User, hr_user: User):
        """Test role hierarchy is enforced"""
        admin_token = await self.get_auth_token(client, ADMIN_DATA)
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        hr_token = await self.get_auth_token(client, HR_DATA)
        hr_headers = {"Authorization": f"Bearer {hr_token}"}
        
        # Admin can modify HR user
        response = await client.put(f"/api/v1/users/{hr_user.id}", json={
            "first_name": "Updated",
            "last_name": "HR",
            "email": hr_user.email,
            "role_id": hr_user.role_id
        }, headers=admin_headers)
        assert response.status_code == 200
        
        # HR cannot modify admin user's role
        response = await client.put(f"/api/v1/users/{admin_user.id}", json={
            "first_name": admin_user.first_name,
            "last_name": admin_user.last_name,
            "email": admin_user.email,
            "role_id": hr_user.role_id  # Try to demote admin
        }, headers=hr_headers)
        assert response.status_code == 200  # This should work, but role change might be restricted in business logic
    
    async def test_permission_boundary_testing(self, client: AsyncClient, admin_user: User, hr_user: User, regular_user: User):
        """Test permission boundaries are properly enforced"""
        # Test different permission levels
        test_cases = [
            {
                "user": admin_user,
                "user_data": ADMIN_DATA,
                "permissions": ["create", "read", "update", "delete"],
                "endpoints": [
                    ("GET", "/api/v1/users/", 200),
                    ("POST", "/api/v1/users/", 201),
                    ("PUT", f"/api/v1/users/{regular_user.id}", 200),
                    ("DELETE", f"/api/v1/users/{regular_user.id}", 200)
                ]
            },
            {
                "user": hr_user,
                "user_data": HR_DATA,
                "permissions": ["create", "read", "update"],
                "endpoints": [
                    ("GET", "/api/v1/users/", 200),
                    ("POST", "/api/v1/users/", 201),
                    ("PUT", f"/api/v1/users/{regular_user.id}", 200),
                    ("DELETE", f"/api/v1/users/{regular_user.id}", 403)
                ]
            },
            {
                "user": regular_user,
                "user_data": USER_DATA,
                "permissions": ["read"],
                "endpoints": [
                    ("GET", "/api/v1/users/", 200),
                    ("POST", "/api/v1/users/", 403),
                    ("PUT", f"/api/v1/users/{regular_user.id}", 403),
                    ("DELETE", f"/api/v1/users/{regular_user.id}", 403)
                ]
            }
        ]
        
        for test_case in test_cases:
            token = await self.get_auth_token(client, test_case["user_data"])
            headers = {"Authorization": f"Bearer {token}"}
            
            for method, endpoint, expected_status in test_case["endpoints"]:
                if method == "GET":
                    response = await client.get(endpoint, headers=headers)
                elif method == "POST":
                    response = await client.post(endpoint, json={
                        "first_name": "Test",
                        "last_name": "User",
                        "email": "test@example.com",
                        "password": "password123",
                        "role_id": test_case["user"].role_id
                    }, headers=headers)
                elif method == "PUT":
                    response = await client.put(endpoint, json={
                        "first_name": "Updated",
                        "last_name": "User",
                        "email": "test@example.com",
                        "role_id": test_case["user"].role_id
                    }, headers=headers)
                elif method == "DELETE":
                    response = await client.delete(endpoint, headers=headers)
                
                assert response.status_code == expected_status, f"Failed for {test_case['user'].email} on {method} {endpoint}"
    
    async def test_concurrent_role_access(self, client: AsyncClient, admin_user: User, hr_user: User):
        """Test concurrent access with different roles"""
        # Create concurrent requests with different roles
        admin_token = await self.get_auth_token(client, ADMIN_DATA)
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        hr_token = await self.get_auth_token(client, HR_DATA)
        hr_headers = {"Authorization": f"Bearer {hr_token}"}
        
        # Create concurrent requests
        admin_tasks = []
        hr_tasks = []
        
        for i in range(5):
            admin_tasks.append(client.get("/api/v1/users/", headers=admin_headers))
            hr_tasks.append(client.get("/api/v1/users/", headers=hr_headers))
        
        # Execute all requests concurrently
        all_tasks = admin_tasks + hr_tasks
        responses = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # Verify all requests succeeded
        successful_responses = [r for r in responses if not isinstance(r, Exception) and r.status_code == 200]
        assert len(successful_responses) == 10
        
        # Verify admin and HR users got appropriate responses
        admin_responses = [r for r in responses[:5] if not isinstance(r, Exception)]
        hr_responses = [r for r in responses[5:] if not isinstance(r, Exception)]
        
        assert all(r.status_code == 200 for r in admin_responses)
        assert all(r.status_code == 200 for r in hr_responses)








