import warnings
from typing import Annotated, Any, List, Literal

from pydantic import (
    AliasChoices,
    AnyUrl,
    BeforeValidator,
    Field,
    HttpUrl,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


DEV_DEFAULT_SECRET = "changethis"


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use local .env file
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        # Never echo rejected values (passwords, URLs with credentials) in errors.
        hide_input_in_errors=True,
    )

    # Must be set explicitly outside ENVIRONMENT=local (enforced below). Locally a fixed
    # development default keeps tokens valid across restarts and --reload.
    SECRET_KEY: str = DEV_DEFAULT_SECRET

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def _empty_secret_is_unset(cls, value: Any) -> Any:
        # pydantic-settings 2.1 does not apply env_ignore_empty, so SECRET_KEY=""
        # would otherwise be accepted as a (very weak) real key.
        if value is None or (isinstance(value, str) and not value.strip()):
            return DEV_DEFAULT_SECRET
        return value
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    API_V1_STR: str = "/api/v1"
    FRONTEND_HOST: str = "http://localhost:3000"
    # ENV is accepted too, because older deployment guides told people to set it.
    # ENVIRONMENT wins when both are set.
    ENVIRONMENT: Literal["local", "staging", "production"] = Field(
        default="local", validation_alias=AliasChoices("ENVIRONMENT", "ENV")
    )

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str = "FileCollab"
    SENTRY_DSN: HttpUrl | None = None
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "12345678"
    POSTGRES_DB: str = "file_collaboration_db"

    # Optional full connection URL, as set by Render, Railway, Heroku and others.
    # When set it replaces the POSTGRES_* variables above.
    DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: Any) -> Any:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        value = value.strip()
        scheme, sep, rest = value.partition("://")
        if not sep or scheme not in ("postgres", "postgresql", "postgresql+psycopg2"):
            raise ValueError(
                "DATABASE_URL must be a PostgreSQL URL "
                "(postgres://, postgresql:// or postgresql+psycopg2://)"
            )
        return f"postgresql+psycopg2://{rest}"

    # File collaboration settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        ".txt", ".md", ".py", ".js", ".html", ".css"]

    # WebSocket settings
    WEBSOCKET_PING_INTERVAL: int = 20
    WEBSOCKET_PING_TIMEOUT: int = 20

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Superuser configuration
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"

    @computed_field
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return str(
            MultiHostUrl.build(
                scheme="postgresql+psycopg2",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    # AWS Configuration
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "eu-north-1"  # Updated to match your .env
    S3_BUCKET_NAME: str = "awsfilecollab"  # Updated to match your .env

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == DEV_DEFAULT_SECRET:
            message = (
                f"{var_name} is not set, so the development default is in use. "
                f"Set {var_name} to a unique secret value for any deployment."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        if not self.DATABASE_URL:  # POSTGRES_PASSWORD is unused when DATABASE_URL is set
            self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)

        return self


settings = Settings()
