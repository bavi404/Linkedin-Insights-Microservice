"""
Configuration management using Pydantic BaseSettings
Centralized application configuration
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "linkedin_insights"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["*"]
    
    # Database
    DATABASE_URL: str
    
    # Scraper
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_RETRY_ATTEMPTS: int = 3
    SCRAPER_HEADLESS: bool = True
    SCRAPER_PAGE_LOAD_TIMEOUT: int = 60000  # milliseconds
    SCRAPER_NAVIGATION_TIMEOUT: int = 30000  # milliseconds
    
    # AI Summary (Optional)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 300
    
    # Redis (Optional)
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_CACHE_TTL: int = 300  # 5 minutes default
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()

