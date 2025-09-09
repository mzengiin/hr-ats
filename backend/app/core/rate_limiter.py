"""
Rate limiting utilities
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException, Request, status
import time

from app.core.config import settings


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.max_requests = settings.RATE_LIMIT_PER_MINUTE
        self.window_seconds = 60
    
    def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed for the given key
        
        Args:
            key: Unique identifier for rate limiting (e.g., IP address)
            
        Returns:
            bool: True if request is allowed, False if rate limited
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Get requests for this key
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key] 
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True
        
        return False
    
    def get_retry_after(self, key: str) -> int:
        """
        Get seconds until next request is allowed
        
        Args:
            key: Unique identifier for rate limiting
            
        Returns:
            int: Seconds until next request is allowed
        """
        if key not in self.requests or not self.requests[key]:
            return 0
        
        oldest_request = min(self.requests[key])
        retry_after = int(oldest_request + self.window_seconds - time.time())
        return max(0, retry_after)
    
    def reset(self, key: str) -> None:
        """
        Reset rate limit for a key
        
        Args:
            key: Unique identifier to reset
        """
        if key in self.requests:
            del self.requests[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Client IP address
    """
    # Check for forwarded IP first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    return request.client.host if request.client else "unknown"


def check_rate_limit(request: Request) -> None:
    """
    Check rate limit for the request
    
    Args:
        request: FastAPI request object
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    client_ip = get_client_ip(request)
    
    if not rate_limiter.is_allowed(client_ip):
        retry_after = rate_limiter.get_retry_after(client_ip)
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )


def reset_rate_limit(request: Request) -> None:
    """
    Reset rate limit for the request
    
    Args:
        request: FastAPI request object
    """
    client_ip = get_client_ip(request)
    rate_limiter.reset(client_ip)


class LoginAttemptTracker:
    """Track failed login attempts for additional security"""
    
    def __init__(self):
        self.failed_attempts: Dict[str, list] = {}
        self.max_failed_attempts = 5
        self.lockout_duration = 300  # 5 minutes
    
    def record_failed_attempt(self, key: str) -> None:
        """
        Record a failed login attempt
        
        Args:
            key: Unique identifier (usually email)
        """
        now = time.time()
        
        if key not in self.failed_attempts:
            self.failed_attempts[key] = []
        
        self.failed_attempts[key].append(now)
    
    def record_successful_attempt(self, key: str) -> None:
        """
        Record a successful login attempt (clear failed attempts)
        
        Args:
            key: Unique identifier (usually email)
        """
        if key in self.failed_attempts:
            del self.failed_attempts[key]
    
    def is_locked_out(self, key: str) -> bool:
        """
        Check if account is locked out due to too many failed attempts
        
        Args:
            key: Unique identifier (usually email)
            
        Returns:
            bool: True if locked out, False otherwise
        """
        if key not in self.failed_attempts:
            return False
        
        now = time.time()
        recent_attempts = [
            attempt for attempt in self.failed_attempts[key]
            if now - attempt < self.lockout_duration
        ]
        
        return len(recent_attempts) >= self.max_failed_attempts
    
    def get_lockout_remaining(self, key: str) -> int:
        """
        Get seconds remaining in lockout
        
        Args:
            key: Unique identifier (usually email)
            
        Returns:
            int: Seconds remaining in lockout
        """
        if not self.is_locked_out(key):
            return 0
        
        now = time.time()
        oldest_recent_attempt = min([
            attempt for attempt in self.failed_attempts[key]
            if now - attempt < self.lockout_duration
        ])
        
        remaining = int(oldest_recent_attempt + self.lockout_duration - now)
        return max(0, remaining)


# Global login attempt tracker
login_tracker = LoginAttemptTracker()


def check_login_attempts(email: str) -> None:
    """
    Check if login attempts are allowed for email
    
    Args:
        email: User email address
        
    Raises:
        HTTPException: If account is locked out
    """
    if login_tracker.is_locked_out(email):
        remaining = login_tracker.get_lockout_remaining(email)
        
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked due to too many failed attempts. Try again in {remaining} seconds."
        )


def record_login_attempt(email: str, success: bool) -> None:
    """
    Record login attempt
    
    Args:
        email: User email address
        success: Whether login was successful
    """
    if success:
        login_tracker.record_successful_attempt(email)
    else:
        login_tracker.record_failed_attempt(email)









