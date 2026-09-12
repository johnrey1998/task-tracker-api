from pydantic import Field, PostgresDsn, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.exceptions import ConfigurationError

class Settings(BaseSettings):
    app_name: str = "Task Tracker API"
    api_prefix: str = "/api/v1"

    database_url: PostgresDsn = Field(default="postgresql+psycopg://admin:password@localhost:5432/task_tracker", alias="DATABASE_URL")

    jwt_secret: str = Field(default="secret", alias="JWT_SECRET")

    jwt_algorithm: str = "HS256"
    token_expiration_hours: int = 8

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def load_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as error:
        raise ConfigurationError("Application configuration invalid") from error


settings = load_settings()




