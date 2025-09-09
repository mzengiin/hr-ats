"""
Input validation and sanitization utilities
"""
import re
import html
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, validator


class InputValidator:
    """Input validation and sanitization"""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input"""
        if not value:
            return ""
        
        # Remove HTML tags
        value = re.sub(r'<[^>]+>', '', value)
        
        # Escape HTML entities
        value = html.escape(value)
        
        # Remove control characters
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        return value.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number"""
        digits = re.sub(r'\D', '', phone)
        return 7 <= len(digits) <= 15
    
    @staticmethod
    def validate_password_strength(password: str) -> List[str]:
        """Validate password strength"""
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters")
        
        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain uppercase letter")
        
        if not re.search(r'[a-z]', password):
            issues.append("Password must contain lowercase letter")
        
        if not re.search(r'\d', password):
            issues.append("Password must contain number")
        
        return issues


class SecurityValidator:
    """Security-focused validation"""
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """Check for SQL injection patterns"""
        sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)',
            r'(\b(UNION|OR|AND)\b)',
            r'(\b(WHERE|FROM|INTO|VALUES)\b)',
            r'(\b(EXEC|EXECUTE|SP_)\b)',
            r'(\b(SCRIPT|JAVASCRIPT|VBSCRIPT)\b)',
            r'(\b(ONLOAD|ONERROR|ONCLICK)\b)'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def check_xss(value: str) -> bool:
        """Check for XSS patterns"""
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>'
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def sanitize_input(value: str) -> str:
        """Sanitize input for security"""
        if not value:
            return ""
        
        # Remove potential XSS
        value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE)
        value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
        value = re.sub(r'vbscript:', '', value, flags=re.IGNORECASE)
        
        # Remove HTML tags
        value = re.sub(r'<[^>]+>', '', value)
        
        # Escape HTML entities
        value = html.escape(value)
        
        return value.strip()









