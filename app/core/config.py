from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str
    DB_ECHO: bool = False

    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    TEST_DATABASE_URL: str = ""

    TELEGRAM_BOT_TOKEN: str = ""

    HOST: str = "localhost"
    PORT: int = 8000
    API_PREFIX: str = "/api"


settings = Settings()
