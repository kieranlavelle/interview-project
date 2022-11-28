from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    DATABASE_URL = "postgresql://postgres:password@localhost:5432/postgres"


settings = Settings()

__all__ = ["settings"]
