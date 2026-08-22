import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5433
    DB_NAME: str = "integration_db"

    # Mocks authentication
    REST_SOURCE_API_KEY: str = "test_rest_key_123"
    XML_SOURCE_USERNAME: str = "admin"
    XML_SOURCE_PASSWORD: str = "secret_xml_123"
    WEBHOOK_SIGNATURE_KEY: str = "webhook_secret_key_abc"

    # CSV Directory
    CSV_DROP_DIR: str = "./csv_drop"

    # Application ports
    FASTAPI_HOST: str = "127.0.0.1"
    FASTAPI_PORT: int = 8001
    STREAMLIT_PORT: int = 8502

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
