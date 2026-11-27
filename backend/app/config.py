# Application configuration: at startup, compares keys and values from .env and
# environment variables against the expected Settings contract (validates required
# fields, coerces types, and checks allowed values via Pydantic).
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Applications settings, read once from the environment at startup"""

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Where to read variables from (.env one level up) and how to handle unknown keys:
    # extra="ignore" silently ignores variables not defined on Settings.
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    # Logging level: only the listed strings are allowed (case-sensitive),
    # defaulting to "INFO".
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
