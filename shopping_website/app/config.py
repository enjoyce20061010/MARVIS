from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_hostname: str
    database_port: str
    database_password: Optional[str] = os.getenv("DATABASE_PASSWORD")
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

settings = Settings()

if not settings.database_password:
    # If the environment variable is not set, load it from the .env file again
    # This ensures that the .env file is used as a fallback.
    temp_settings = Settings(_env_file=".env")
    settings.database_password = temp_settings.database_password