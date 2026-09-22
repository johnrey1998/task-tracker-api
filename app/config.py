from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.exceptions import ConfigurationError

class Settings(BaseSettings):
    app_name: str = "Task Tracker API"
    api_prefix: str = "/api/v1"

    postgres_user: str = "admin"
    postgres_password: str = "password"
    postgres_db: str = "task_tracker"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    jwt_secret: str = "secret"
    jwt_algorithm: str = "HS256"
    token_expiration_hours: int = 8

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)


settings = Settings()




