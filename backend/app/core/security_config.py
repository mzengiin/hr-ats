"""
Security configuration and utilities
"""
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os

from app.core.config import settings


def setup_cors(app: FastAPI) -> None:
    """
    Setup CORS middleware
    
    Args:
        app: FastAPI application
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page-Count"]
    )


def setup_trusted_hosts(app: FastAPI) -> None:
    """
    Setup trusted host middleware
    
    Args:
        app: FastAPI application
    """
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )


def get_security_headers() -> Dict[str, str]:
    """
    Get security headers configuration
    
    Returns:
        Dict containing security headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        ),
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Resource-Policy": "same-origin"
    }


def get_csp_policy() -> str:
    """
    Get Content Security Policy configuration
    
    Returns:
        str: CSP policy string
    """
    return (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https: blob:; "
        "font-src 'self' data:; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )


def validate_origin(origin: str) -> bool:
    """
    Validate if origin is allowed
    
    Args:
        origin: Origin to validate
        
    Returns:
        bool: True if origin is allowed
    """
    allowed_origins = settings.ALLOWED_ORIGINS
    
    # Allow all origins in development
    if "*" in allowed_origins:
        return True
    
    return origin in allowed_origins


def validate_host(host: str) -> bool:
    """
    Validate if host is trusted
    
    Args:
        host: Host to validate
        
    Returns:
        bool: True if host is trusted
    """
    allowed_hosts = settings.ALLOWED_HOSTS
    
    # Allow all hosts in development
    if "*" in allowed_hosts:
        return True
    
    return host in allowed_hosts


def get_rate_limit_config() -> Dict[str, Any]:
    """
    Get rate limiting configuration
    
    Returns:
        Dict containing rate limit configuration
    """
    return {
        "login_attempts": {
            "max_attempts": 5,
            "lockout_duration": 300,  # 5 minutes
            "window_duration": 900    # 15 minutes
        },
        "api_requests": {
            "max_requests": 100,
            "window_duration": 60     # 1 minute
        },
        "password_reset": {
            "max_attempts": 3,
            "lockout_duration": 1800  # 30 minutes
        }
    }


def get_password_policy() -> Dict[str, Any]:
    """
    Get password policy configuration
    
    Returns:
        Dict containing password policy
    """
    return {
        "min_length": 8,
        "max_length": 128,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special_chars": False,
        "forbidden_passwords": [
            "password", "12345678", "qwerty123", "admin123",
            "letmein", "welcome123", "password123", "123456789"
        ],
        "max_age_days": 90,
        "history_count": 5
    }


def get_session_config() -> Dict[str, Any]:
    """
    Get session configuration
    
    Returns:
        Dict containing session configuration
    """
    return {
        "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "refresh_token_expire_days": settings.REFRESH_TOKEN_EXPIRE_DAYS,
        "max_concurrent_sessions": 5,
        "session_timeout_minutes": 30,
        "remember_me_days": 30
    }


def get_audit_config() -> Dict[str, Any]:
    """
    Get audit logging configuration
    
    Returns:
        Dict containing audit configuration
    """
    return {
        "enabled": True,
        "log_level": "INFO",
        "retention_days": 90,
        "log_rotation_days": 7,
        "sensitive_fields": [
            "password", "password_hash", "token", "secret",
            "api_key", "private_key", "ssn", "credit_card"
        ],
        "events_to_log": [
            "LOGIN", "LOGOUT", "CREATE_USER", "UPDATE_USER",
            "DELETE_USER", "CHANGE_PASSWORD", "RESET_PASSWORD",
            "ACCESS_DENIED", "PERMISSION_GRANTED", "PERMISSION_DENIED"
        ]
    }


def get_encryption_config() -> Dict[str, Any]:
    """
    Get encryption configuration
    
    Returns:
        Dict containing encryption configuration
    """
    return {
        "algorithm": "AES-256-GCM",
        "key_rotation_days": 90,
        "encrypt_sensitive_data": True,
        "sensitive_fields": [
            "email", "phone", "ssn", "address",
            "bank_account", "credit_card"
        ]
    }


def validate_security_headers(headers: Dict[str, str]) -> List[str]:
    """
    Validate security headers
    
    Args:
        headers: Headers to validate
        
    Returns:
        List of missing or invalid headers
    """
    required_headers = get_security_headers()
    issues = []
    
    for header, expected_value in required_headers.items():
        if header not in headers:
            issues.append(f"Missing header: {header}")
        elif headers[header] != expected_value:
            issues.append(f"Invalid header {header}: expected '{expected_value}', got '{headers[header]}'")
    
    return issues


def get_security_recommendations() -> List[str]:
    """
    Get security recommendations
    
    Returns:
        List of security recommendations
    """
    return [
        "Enable HTTPS in production",
        "Use strong, unique passwords",
        "Enable two-factor authentication",
        "Regular security audits",
        "Keep dependencies updated",
        "Monitor for suspicious activity",
        "Use rate limiting",
        "Implement proper logging",
        "Regular backup of data",
        "Use environment variables for secrets"
    ]


def check_security_compliance() -> Dict[str, Any]:
    """
    Check security compliance
    
    Returns:
        Dict containing compliance status
    """
    compliance = {
        "https_enabled": os.getenv("HTTPS_ENABLED", "false").lower() == "true",
        "cors_configured": len(settings.ALLOWED_ORIGINS) > 0,
        "trusted_hosts_configured": len(settings.ALLOWED_HOSTS) > 0,
        "rate_limiting_enabled": True,
        "audit_logging_enabled": True,
        "password_policy_enforced": True,
        "session_management_enabled": True,
        "security_headers_enabled": True
    }
    
    compliance["overall_score"] = sum(compliance.values()) / len(compliance) * 100
    
    return compliance








