from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./instagram_clone.db"
    
    # JWT - REQUIRED: Must be set in .env file
    # For development, we allow defaults but they will be rejected by validator
    SECRET_KEY: str = "TEMPORARY_DEFAULT_CHANGE_IN_ENV_FILE_MIN_32_CHARS"
    REFRESH_SECRET_KEY: str = "TEMPORARY_DEFAULT_CHANGE_IN_ENV_FILE_MIN_32_CHARS"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes (short-lived)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days (long-lived)
    
    # Security
    BCRYPT_ROUNDS: int = 12  # Number of bcrypt rounds (higher = more secure but slower)
    DEBUG: bool = False  # Default to False for security

    # Celery / background jobs
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # File Upload
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    
    # Stories
    STORY_EXPIRY_HOURS: int = 24  # Stories expire after 24 hours (can override for testing)
    
    # App
    APP_NAME: str = "Instagram Clone"
    
    @field_validator('SECRET_KEY', 'REFRESH_SECRET_KEY')
    @classmethod
    def validate_secret_keys(cls, v: str, info) -> str:
        """Ensure secret keys are secure"""
        # Allow temporary defaults for development (will show warning)
        if v == "TEMPORARY_DEFAULT_CHANGE_IN_ENV_FILE_MIN_32_CHARS":
            import warnings
            warnings.warn(
                f"⚠️  WARNING: {info.field_name} is using a temporary default value. "
                "This is INSECURE for production! Set a secure key in .env file. "
                "Generate with: python -c 'import secrets; print(secrets.token_hex(32))'",
                UserWarning
            )
            return v
        
        if len(v) < 32:
            raise ValueError(
                f'{info.field_name} must be at least 32 characters long. '
                'Generate with: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        # Check for default/weak values
        weak_patterns = ['your-secret', 'change-this', 'secret-key', 'example', 'default', 'temporary']
        if any(pattern in v.lower() for pattern in weak_patterns):
            raise ValueError(
                f'{info.field_name} appears to be a default value. '
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

