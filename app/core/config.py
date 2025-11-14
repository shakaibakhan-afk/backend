from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./instagram_clone.db"
    
    # JWT - IMPORTANT: Change SECRET_KEY in production!
    SECRET_KEY: str = "your-secret-key-change-this-in-production-use-long-random-string-min-32-chars"
    REFRESH_SECRET_KEY: str = "your-refresh-secret-key-change-this-in-production-different-from-access"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes (short-lived)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days (long-lived)
    
    # Security
    BCRYPT_ROUNDS: int = 12  # Number of bcrypt rounds (higher = more secure but slower)

    # Celery / background jobs
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # File Upload
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    
    # App
    APP_NAME: str = "Instagram Clone"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()

