"""DATABASE_URL and ENV support (hosting platforms such as Render and Railway set these)."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings

SECRET = "a-real-secret-value-1234567890"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ("DATABASE_URL", "ENV", "ENVIRONMENT", "SECRET_KEY", "POSTGRES_PASSWORD"):
        monkeypatch.delenv(name, raising=False)


def make(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)


def test_without_database_url_builds_from_postgres_parts():
    settings = make(POSTGRES_SERVER="db.internal", POSTGRES_PORT=5432, POSTGRES_PASSWORD="pw")
    assert settings.SQLALCHEMY_DATABASE_URI == (
        "postgresql+psycopg2://postgres:pw@db.internal:5432/file_collaboration_db"
    )


@pytest.mark.parametrize(
    "given",
    [
        "postgres://u:p@host.example:6543/app",
        "postgresql://u:p@host.example:6543/app",
        "postgresql+psycopg2://u:p@host.example:6543/app",
    ],
)
def test_database_url_wins_and_gets_the_psycopg2_driver(monkeypatch, given):
    monkeypatch.setenv("DATABASE_URL", given)
    settings = make(POSTGRES_SERVER="ignored")
    assert settings.SQLALCHEMY_DATABASE_URI == "postgresql+psycopg2://u:p@host.example:6543/app"


def test_database_url_keeps_query_parameters(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@h:5432/app?sslmode=require")
    assert make().SQLALCHEMY_DATABASE_URI == "postgresql+psycopg2://u:p@h:5432/app?sslmode=require"


def test_empty_database_url_is_ignored(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    assert make(POSTGRES_PASSWORD="pw").SQLALCHEMY_DATABASE_URI.startswith(
        "postgresql+psycopg2://postgres:pw@localhost:5433/"
    )


def test_non_postgres_database_url_is_rejected(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql://u:p@h/app")
    with pytest.raises(ValidationError, match="DATABASE_URL"):
        make()


def test_deployed_with_database_url_does_not_need_postgres_password(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@h:5432/app")
    settings = make(ENVIRONMENT="production", SECRET_KEY=SECRET, POSTGRES_PASSWORD="changethis")
    assert settings.SQLALCHEMY_DATABASE_URI.startswith("postgresql+psycopg2://")


def test_deployed_without_database_url_still_rejects_default_postgres_password():
    with pytest.raises(ValidationError, match="POSTGRES_PASSWORD"):
        make(ENVIRONMENT="production", SECRET_KEY=SECRET, POSTGRES_PASSWORD="changethis")


def test_env_is_accepted_as_environment(monkeypatch):
    # The old deployment guides told people to set ENV=production. That must not
    # silently fall back to local mode, where the development SECRET_KEY is allowed.
    monkeypatch.setenv("ENV", "production")
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        make()


def test_environment_takes_priority_over_env(monkeypatch):
    monkeypatch.setenv("ENV", "local")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", SECRET)
    assert make().ENVIRONMENT == "production"


def test_rejected_database_url_is_not_echoed(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql://u:hunter2-secret@h/app")
    with pytest.raises(ValidationError) as exc:
        make()
    assert "hunter2-secret" not in str(exc.value)
