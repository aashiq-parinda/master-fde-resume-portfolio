import os
import secrets
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.utils.logger import get_logger

logger = get_logger("config")

class Settings(BaseSettings):
    ENV: str = "development"
    PORT: int = 8000
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "factory_db"
    DB_USER: str = "factory_user"
    DB_PASSWORD: str = ""  # Should be set in env
    DB_ADMIN_USER: str = "postgres"
    DB_ADMIN_PASSWORD: str = ""
    
    # LLM
    GEMINI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def validate_secrets(self):
        """Verify password and secret keys exist, fallback with warnings if in development."""
        if not self.DB_PASSWORD:
            if self.ENV == "development":
                # Fallback to ephemeral secret for sandbox
                logger.warning("Generating ephemeral DB_PASSWORD. Instance-isolated!")
                self.DB_PASSWORD = secrets.token_hex(16)
            else:
                raise ValueError("DB_PASSWORD must be provided in production environment!")
        
        if not self.GEMINI_API_KEY or self.GEMINI_API_KEY == "your_gemini_api_key_here" or not self.GEMINI_API_KEY.strip():
            logger.warning(
                "GEMINI_API_KEY is not configured (or is placeholder). The AI Diagnostic Assistant will run in MOCK mode."
            )
            self.GEMINI_API_KEY = None

# Create singleton instance
settings = Settings()
settings.validate_secrets()
