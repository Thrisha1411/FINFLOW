from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinFlow AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "finflow-super-secure-production-ready-secret-key-32charsmin!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"
    
    # Database - default to sqlite file in development/testing, can be overridden with Postgres URL
    DATABASE_URL: str = "sqlite:///./finflow.db"
    
    # Redis (set in production/Docker via environment variable)
    REDIS_URL: Optional[str] = None
    
    # Kafka (set in production/Docker via environment variable)
    KAFKA_BOOTSTRAP_SERVERS: Optional[str] = None
    
    # AI / LLM configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # 2FA Settings
    TOTP_ISSUER: str = "FinFlow AI"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 120

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
