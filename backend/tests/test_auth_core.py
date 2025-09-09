"""
Tests for authentication core functionality
"""
import pytest
from datetime import datetime, timedelta
from jose import JWTError
import uuid

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password,
    TokenData
)


class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        assert len(hashed) > 0
        
        # Should be able to verify correct password
        assert verify_password(password, hashed) is True
        
        # Should reject incorrect password
        assert verify_password("wrong_password", hashed) is False
    
    def test_password_hashing_consistency(self):
        """Test that same password produces different hashes (salt)"""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokenGeneration:
    """Test JWT token generation"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        user_id = str(uuid.uuid4())
        token = create_access_token(data={"sub": user_id})
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        user_id = str(uuid.uuid4())
        token = create_refresh_token(data={"sub": user_id})
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_access_token_expiration(self):
        """Test access token has correct expiration"""
        user_id = str(uuid.uuid4())
        token = create_access_token(data={"sub": user_id})
        
        # Decode token to check expiration
        from jose import jwt
        from app.core.config import settings
        
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        exp = payload.get("exp")
        assert exp is not None
        
        # Check expiration is within expected range (15 minutes)
        now = datetime.utcnow().timestamp()
        exp_time = datetime.fromtimestamp(exp)
        expected_exp = datetime.utcnow() + timedelta(minutes=15)
        
        # Should be within 1 minute of expected expiration
        time_diff = abs((exp_time - expected_exp).total_seconds())
        assert time_diff < 60
    
    def test_refresh_token_expiration(self):
        """Test refresh token has correct expiration"""
        user_id = str(uuid.uuid4())
        token = create_refresh_token(data={"sub": user_id})
        
        # Decode token to check expiration
        from jose import jwt
        from app.core.config import settings
        
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        exp = payload.get("exp")
        assert exp is not None
        
        # Check expiration is within expected range (7 days)
        now = datetime.utcnow().timestamp()
        exp_time = datetime.fromtimestamp(exp)
        expected_exp = datetime.utcnow() + timedelta(days=7)
        
        # Should be within 1 hour of expected expiration
        time_diff = abs((exp_time - expected_exp).total_seconds())
        assert time_diff < 3600


class TestJWTTokenValidation:
    """Test JWT token validation"""
    
    def test_verify_valid_access_token(self):
        """Test verifying valid access token"""
        user_id = str(uuid.uuid4())
        token = create_access_token(data={"sub": user_id})
        
        token_data = verify_token(token)
        assert token_data is not None
        assert token_data.sub == user_id
    
    def test_verify_valid_refresh_token(self):
        """Test verifying valid refresh token"""
        user_id = str(uuid.uuid4())
        token = create_refresh_token(data={"sub": user_id})
        
        token_data = verify_token(token)
        assert token_data is not None
        assert token_data.sub == user_id
    
    def test_verify_invalid_token(self):
        """Test verifying invalid token"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(JWTError):
            verify_token(invalid_token)
    
    def test_verify_expired_token(self):
        """Test verifying expired token"""
        user_id = str(uuid.uuid4())
        
        # Create token with past expiration
        from jose import jwt
        from app.core.config import settings
        
        expired_time = datetime.utcnow() - timedelta(hours=1)
        payload = {
            "sub": user_id,
            "exp": expired_time.timestamp()
        }
        
        expired_token = jwt.encode(
            payload, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        with pytest.raises(JWTError):
            verify_token(expired_token)
    
    def test_verify_token_wrong_secret(self):
        """Test verifying token with wrong secret"""
        user_id = str(uuid.uuid4())
        
        # Create token with different secret
        from jose import jwt
        
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=15)
        }
        
        wrong_secret_token = jwt.encode(
            payload, 
            "wrong_secret", 
            algorithm="HS256"
        )
        
        with pytest.raises(JWTError):
            verify_token(wrong_secret_token)


class TestTokenData:
    """Test TokenData model"""
    
    def test_token_data_creation(self):
        """Test TokenData model creation"""
        user_id = str(uuid.uuid4())
        token_data = TokenData(sub=user_id)
        
        assert token_data.sub == user_id
    
    def test_token_data_optional_fields(self):
        """Test TokenData with optional fields"""
        user_id = str(uuid.uuid4())
        token_data = TokenData(
            sub=user_id,
            exp=datetime.utcnow() + timedelta(minutes=15)
        )
        
        assert token_data.sub == user_id
        assert token_data.exp is not None


class TestSecurityIntegration:
    """Test security features integration"""
    
    def test_password_and_token_workflow(self):
        """Test complete password and token workflow"""
        # 1. Hash password
        password = "secure_password_123"
        hashed_password = get_password_hash(password)
        
        # 2. Verify password
        assert verify_password(password, hashed_password) is True
        
        # 3. Create token for user
        user_id = str(uuid.uuid4())
        access_token = create_access_token(data={"sub": user_id})
        refresh_token = create_refresh_token(data={"sub": user_id})
        
        # 4. Verify tokens
        access_data = verify_token(access_token)
        refresh_data = verify_token(refresh_token)
        
        assert access_data.sub == user_id
        assert refresh_data.sub == user_id
    
    def test_token_rotation_security(self):
        """Test that tokens are unique each time"""
        user_id = str(uuid.uuid4())
        
        # Create multiple tokens
        token1 = create_access_token(data={"sub": user_id})
        token2 = create_access_token(data={"sub": user_id})
        
        # Tokens should be different
        assert token1 != token2
        
        # But both should be valid
        data1 = verify_token(token1)
        data2 = verify_token(token2)
        
        assert data1.sub == user_id
        assert data2.sub == user_id









