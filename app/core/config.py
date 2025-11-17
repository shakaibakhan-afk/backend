from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./instagram_clone.db"
    
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    BCRYPT_ROUNDS: int = 12
    DEBUG: bool = False

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    MAX_FILE_SIZE: int = 5 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    
    STORY_EXPIRY_HOURS: int = 24
    APP_NAME: str = "Instagram Clone"
    
    @field_validator('SECRET_KEY', 'REFRESH_SECRET_KEY')
    @classmethod
    def validate_secret_keys(cls, v: str, info) -> str:
        """Ensure secret keys are secure and loaded from .env"""
        if not v or len(v.strip()) == 0:
            raise ValueError(
                f'{info.field_name} is required and must be set in .env file. '
                'Generate with: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        
        if len(v) < 32:
            raise ValueError(
                f'{info.field_name} must be at least 32 characters long. '
                'Generate with: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        
        weak_patterns = ['your-secret', 'change-this', 'secret-key', 'example', 'default', 'temporary', 'change_this', 'change_this_use_openssl']
        if any(pattern in v.lower() for pattern in weak_patterns):
            raise ValueError(
                f'{info.field_name} appears to be a default/placeholder value. '
                'Generate a secure key with: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        return v
    
    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format"""
        if not v or not v.startswith(('sqlite:', 'postgresql:', 'mysql:', 'postgresql+psycopg2:')):
            raise ValueError('DATABASE_URL must be a valid database connection string')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

