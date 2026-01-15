"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List, Union
import json

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Sentiment to Sprint"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API Keys
    SERPAPI_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    TASK_TTL_SECONDS: int = 86400  # 24 hours
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/scraper_api.log"
   
    
    # Scraping Configuration
    MAX_REDDIT_PAGES: int = 50
    MAX_REVIEWS_APPLE: int = 199
    MAX_REVIEWS_GOOGLE: int = 199
    REDDIT_CONCURRENT_LIMIT: int = 5
    REDDIT_DELAY_MIN: float = 2.0
    REDDIT_DELAY_MAX: float = 4.0
    
    # Gemini Configuration
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"
    GEMINI_MAX_TOKENS: int = 200000
    
    # CORS
    CORS_ORIGINS: Union[str, list[str]] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"
    
    def cors_origins_list(self) -> List[str]:
        # allow JSON list string like ["https://..."]
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        s = str(self.CORS_ORIGINS).strip()
        if s == "*":
            return ["*"]
        try:
            return json.loads(s)
        except Exception:
            return [x.strip() for x in s.split(",") if x.strip()]

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()