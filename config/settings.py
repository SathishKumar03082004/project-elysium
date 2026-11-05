from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    APP_NAME: str = "Project Elysium"
    APP_VERSION: str = "0.1.0"

    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "sqlite:///./data/elysium.db"

    OPENAI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        extra="ignore"
    )


settings = Settings()


def load_yaml(filename: str) -> dict:

    file_path = ROOT_DIR / "config" / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)