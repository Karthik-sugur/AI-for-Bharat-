"""
Configuration settings for LandLedger Backend
Environment-based configuration with AWS service settings
"""

import os
from functools import lru_cache
try:
    from pydantic_settings import BaseSettings  # type: ignore
except ImportError:
    from pydantic import BaseSettings  # type: ignore
from typing import Optional


class Settings(BaseSettings):  # type: ignore
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "LandLedger"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Amazon Bedrock
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    BEDROCK_MAX_TOKENS: int = 4000
    
    # Amazon S3
    S3_BUCKET_NAME: str = "landledger-documents"
    S3_PRESIGNED_URL_EXPIRY: int = 86400  # 24 hours
    
    # Amazon DynamoDB
    DYNAMODB_TABLE_NAME: str = "landledger-cache"
    DYNAMODB_TTL_HOURS: int = 24
    
    # Amazon Polly
    POLLY_VOICE_ENGLISH: str = "Joanna"
    POLLY_VOICE_HINDI: str = "Aditi"
    POLLY_OUTPUT_FORMAT: str = "mp3"
    
    # API Configuration
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
