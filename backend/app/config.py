from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Applications settings, read once from the environment at startup"""

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")