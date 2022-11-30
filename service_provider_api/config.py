from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    DATABASE_HOST: str = "localhost"

    @property
    def DATABASE_URL(self):
        return f"postgresql://postgres:password@{self.DATABASE_HOST}:5432/postgres"


settings = Settings()

__all__ = ["settings"]
