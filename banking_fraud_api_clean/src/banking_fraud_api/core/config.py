"""Core configuration settings for the fraud detection system."""

from typing import Any, Dict, List, Optional
from decimal import Decimal
import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation and type checking."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Banking Fraud Detection API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Enterprise-grade fraud detection system"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = Field(default="default-secret-key-32-chars-long", min_length=32)
    JWT_SECRET_KEY: str = Field(default="default-jwt-secret-key-32-chars", min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./fraud_detection.db")
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_EXPIRE_SECONDS: int = 3600
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Machine Learning
    MODEL_PATH: str = "./models"
    MODEL_VERSION: str = "1.0.0"
    
    # Fraud Detection Thresholds
    FRAUD_THRESHOLD_LOW: float = 0.3
    FRAUD_THRESHOLD_MEDIUM: float = 0.6
    FRAUD_THRESHOLD_HIGH: float = 0.8
    FRAUD_THRESHOLD_CRITICAL: float = 0.9
    
    # Transaction Limits
    MAX_TRANSACTION_AMOUNT: Decimal = Decimal("100000.00")
    SUSPICIOUS_AMOUNT_THRESHOLD: Decimal = Decimal("10000.00")
    HIGH_AMOUNT_THRESHOLD: Decimal = Decimal("5000.00")
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Model Ensemble Configuration
    ENSEMBLE_WEIGHTS: Dict[str, float] = {
        "xgboost": 0.4,
        "lightgbm": 0.3,
        "random_forest": 0.3
    }
    
    # Feature Engineering
    ENABLE_BEHAVIORAL_FEATURES: bool = True
    ENABLE_TEMPORAL_FEATURES: bool = True
    ENABLE_GEOLOCATION_FEATURES: bool = True
    ENABLE_DEVICE_FINGERPRINTING: bool = True
    
    @field_validator("FRAUD_THRESHOLD_LOW", "FRAUD_THRESHOLD_MEDIUM", 
                    "FRAUD_THRESHOLD_HIGH", "FRAUD_THRESHOLD_CRITICAL")
    @classmethod
    def validate_threshold(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Fraud threshold must be between 0 and 1")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """Get settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
