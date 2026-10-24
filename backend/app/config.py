from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    MONGODB_URI: str = ""
    MONGODB_DATABASE: str = "shopsense_ai"
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    CLARIFICATION_THRESHOLD: float = 0.65

    model_config = SettingsConfigDict(
        env_file=BACKEND_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def groq_configured(self) -> bool:
        return bool(self.GROQ_API_KEY and self.GROQ_MODEL)

    @property
    def mongo_configured(self) -> bool:
        return bool(self.MONGODB_URI)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
