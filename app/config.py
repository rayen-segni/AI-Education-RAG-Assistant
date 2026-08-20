from pathlib import Path
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamically resolve project root directory (app/config.py -> app/ -> root)
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # PostgreSQL Configuration
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASS: str = "rayen"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    
    # Local Ollama AI Engine Settings
    OLLAMA_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text:latest"
    LARGE_LANGUAGE_MODEL: str = "qwen2.5:0.5b"
    CROSS_ENCODER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L6-v2"

    # Compute PostgreSQL DSN connection string
    @computed_field
    def database_url(self) -> str:
        return f"dbname={self.DB_NAME} user={self.DB_USER} password={self.DB_PASS} host={self.DB_HOST} port={self.DB_PORT}"

    # Tell Pydantic to read directly from root .env file
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()