from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Code Migration Platform - Backend"
    STORAGE_DIR: Path = Path(__file__).parent.parent.parent / "storage"
    PROJECTS_DIR: Path = STORAGE_DIR / "projects"
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None
    
    # AI Engine
    GEMINI_API_KEY: str | None = None

    # Database
    MONGODB_URL: str | None = None
    MONGODB_DB: str = "Code_Migration_V1"

    # Email SMTP (Gmail)
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_HOST_USER: str | None = None
    EMAIL_HOST_PASSWORD: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
