"""
Configuration management using Pydantic BaseSettings
Centralized application configuration
"""
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
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()

