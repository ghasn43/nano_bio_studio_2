"""
Configuration Module

Centralized configuration for ML module including models, database, API, and logging.
"""

import os
import logging
from typing import List, Optional
from enum import Enum

# Try new pydantic v2 structure first, fallback to v1
try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings  # pydantic v1 fallback
    except ImportError:
        # Minimal fallback if pydantic not available
        class BaseSettings:
            class Config:
                env_file = ".env"
                case_sensitive = False


class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENV: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///ml_module.db"
    DATABASE_ECHO: bool = False
    
    # API
    API_TITLE: str = "NanoBio ML API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # ML Models
    MODELS_DIR: str = "models_store"
    MODEL_REGISTRY_PATH: str = "model_registry.json"
    SUPPORTED_MODEL_TYPES: List[str] = [
        "linear_regression",
        "random_forest",
        "gradient_boosting",
        "neural_network",
        "logistic_regression",
        "svm",
    ]
    
    # Training
    DEFAULT_TEST_SPLIT: float = 0.2
    DEFAULT_RANDOM_STATE: int = 42
    DEFAULT_MAX_FEATURES: Optional[int] = None
    DEFAULT_N_ESTIMATORS: int = 100
    DEFAULT_MAX_DEPTH: Optional[int] = 10
    DEFAULT_LEARNING_RATE: float = 0.01
    
    # Scaling
    SCALE_NUMERIC_FEATURES: bool = True
    SCALER_TYPE: str = "standard"  # 'standard' or 'minmax'
    
    # Feature Engineering
    ENABLE_POLYNOMIAL_FEATURES: bool = False
    POLYNOMIAL_DEGREE: int = 2
    ENABLE_INTERACTION_FEATURES: bool = False
    
    # Data
    MAX_UPLOAD_SIZE_MB: int = 100
    HANDLE_MISSING_VALUES: str = "mean"  # 'mean', 'median', 'drop'
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Performance
    N_JOBS: int = -1  # Use all available cores
    
    # Caching
    ENABLE_CACHE: bool = True
    CACHE_DIR: str = ".cache"
    CACHE_TTL_SECONDS: int = 3600
    
    # Evaluation
    CV_FOLDS: int = 5
    RANDOM_SEARCH_N_ITER: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def configure_logging():
    """Configure logging based on settings"""
    settings = get_settings()
    
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Basic config
    logging.basicConfig(
        level=log_level,
        format=settings.LOG_FORMAT,
    )
    
    # File handler if configured
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(log_level)
        formatter = logging.Formatter(settings.LOG_FORMAT)
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
    
    return logging.getLogger(__name__)


# Logging configuration on module import
logger = configure_logging()
