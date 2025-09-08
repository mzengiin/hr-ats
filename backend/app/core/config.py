"""
Application configuration
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost/cvflow_db"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS - Basit ve etkili çözüm
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0", "*"]
    
    # Debug
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 5
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            # Virgülle ayrılmış string'i listeye çevir
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"


settings = Settings()
