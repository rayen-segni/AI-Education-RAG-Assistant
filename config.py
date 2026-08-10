from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    # Core system rules
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASS: str = "rayen"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    
    OLLAMA_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text:latest"
    LARGE_LANGUAGE_MODEL: str = "qwen2.5:0.5b"

    # Nately construct our connection contract string using Pydantic fields
    @computed_field
    def database_url(self) -> str:
        return f"dbname={self.DB_NAME} user={self.DB_USER} password={self.DB_PASS} host={self.DB_HOST} port={self.DB_PORT}"

    # Tell Pydantic to read directly from local text environments
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()