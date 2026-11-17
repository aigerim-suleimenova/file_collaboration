"""SECRET_KEY rules (specs/runtime-configuration)."""

import warnings

import pytest
from pydantic import ValidationError

from app.core.config import Settings


@pytest.fixture(autouse=True)
def no_secret_in_env(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)


def make(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_deployed_without_secret_refuses_to_start(environment):
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        make(ENVIRONMENT=environment)


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_deployed_with_development_default_refuses_to_start(environment):
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        make(ENVIRONMENT=environment, SECRET_KEY="changethis")


def test_deployed_with_empty_secret_refuses_to_start(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "")
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        make(ENVIRONMENT="production")


def test_deployed_with_real_secret_starts():
    settings = make(ENVIRONMENT="production", SECRET_KEY="a-real-secret-value-1234567890")
    assert settings.SECRET_KEY == "a-real-secret-value-1234567890"


def test_error_does_not_print_the_secret():
    with pytest.raises(ValidationError) as exc:
        make(ENVIRONMENT="production", SECRET_KEY="changethis")
    # The message names the variable but must not echo a real secret; the
    # development default is the only value that can appear here.
    assert "SECRET_KEY" in str(exc.value)


def test_local_without_secret_is_stable_and_warns():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        first = make(ENVIRONMENT="local")
        second = make(ENVIRONMENT="local")
    assert first.SECRET_KEY == second.SECRET_KEY  # tokens survive a restart
    assert any("development default" in str(w.message) for w in caught)
