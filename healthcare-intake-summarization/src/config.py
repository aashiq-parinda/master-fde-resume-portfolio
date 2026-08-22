import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5434
    DB_NAME: str = "healthcare_db"

    # Gemini LLM API
    GEMINI_API_KEY: str = "your_gemini_api_key_here"

    # Ports
    FASTAPI_HOST: str = "127.0.0.1"
    FASTAPI_PORT: int = 8002
    STREAMLIT_PORT: int = 8503

    def validate_secrets(self) -> None:
        """Sanitizes key placeholders to enforce offline/mock fallback cleanly."""
        if not self.GEMINI_API_KEY or self.GEMINI_API_KEY == "your_gemini_api_key_here":
            # Force to None to trigger mock mode safely
            object.__setattr__(self, 'GEMINI_API_KEY', None)

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
settings.validate_secrets()
