from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/review_intelligence"
    redis_url: str = "redis://localhost:6379/0"
    serpapi_key: str = "demo_key"
    
    class Config:
        env_file = ".env"

settings = Settings()
