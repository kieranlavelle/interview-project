"""Module to hold all of the application configuration settings
for the service.

The Settings class is used to load the configuration settings from
the environment variables. The settings are then used to configure
the application.
"""

from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):

    DATABASE_HOST: str = "localhost"
    DATABASE_PASSWORD: SecretStr = SecretStr("password")
    LOG_LEVEL: str = "INFO"

    @property
    def DATABASE_URL(self) -> str:
        url = "postgresql://postgres:{password}@{host}/postgres"
        return url.format(
            password=self.DATABASE_PASSWORD.get_secret_value(),
            host=self.DATABASE_HOST,
        )


settings = Settings()

__all__ = ["settings"]
