import os
from pathlib import Path
from typing import Literal

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ROOT_DIR / ".." / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    PROJECT_NAME: str = "AutoApply"
    ROOT_DIR: Path = _ROOT_DIR
    CV_DIR_PATH: Path = _ROOT_DIR / "cv"
    HTML_TEMPLATE_PATH: Path = _ROOT_DIR / "career_documents" / "template.html"
    STYLING_PATH: Path = _ROOT_DIR / "career_documents" / "styling.css"
    PDF_ENGINE: str = "weasyprint"
    DEBUG: bool = False
    HEADLESS: bool = False
    LOG_TO_FILE: bool = True
    API_KEY: str
    OPENAI_API_KEY: str
    DB_BACKEND: Literal["sqlite", "postgres"] = "sqlite"
    DB_USERNAME: str | None = (
        None  # TODO: Maybe make this a computed_field or add field_validator
    )
    DB_PASSWORD: str | None = (
        None  # TODO: Maybe make this a computed_field or add field_validator
    )
    DB_HOST: str | None = (
        None  # TODO: Maybe make this a computed_field or add field_validator
    )
    DB_NAME: str = "autojobapp"
    DB_PORT: int = 5432

    # @field_validator("POSTGRES_HOST", mode="before")
    # @classmethod
    # def check_env(cls, value: str) -> str:
    #     if value:
    #         return value
    #     if os.getenv("DOCKER_ENV"):
    #         return "postgres_database"
    #     return "localhost"

    @computed_field
    @property
    def DATABASE_URI(self) -> str:
        if self.DB_BACKEND == "sqlite":
            # TODO: sqlite+aiosqlite
            return f"sqlite:///{_ROOT_DIR / self.DB_NAME}.db"
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        ).encoded_string()


settings = Settings()  # type: ignore
