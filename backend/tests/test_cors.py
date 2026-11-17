"""CORS policy follows configuration (specs/runtime-configuration)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import configure_cors


def app_with(**settings_overrides) -> TestClient:
    settings = Settings(_env_file=None, SECRET_KEY="test-secret-not-default", **settings_overrides)
    app = FastAPI()
    configure_cors(app, settings)

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"ok": "yes"}

    return TestClient(app)


def preflight(client: TestClient, origin: str):
    return client.options(
        "/ping",
        headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
    )


def test_configured_frontend_host_is_allowed():
    client = app_with(ENVIRONMENT="production", FRONTEND_HOST="https://app.example.test")
    res = preflight(client, "https://app.example.test")
    assert res.headers.get("access-control-allow-origin") == "https://app.example.test"


def test_backend_cors_origins_are_allowed():
    client = app_with(
        ENVIRONMENT="production",
        FRONTEND_HOST="https://app.example.test",
        BACKEND_CORS_ORIGINS="https://other.example.test",
    )
    res = preflight(client, "https://other.example.test")
    assert res.headers.get("access-control-allow-origin") == "https://other.example.test"


def test_unknown_origin_rejected_in_production():
    client = app_with(ENVIRONMENT="production", FRONTEND_HOST="https://app.example.test")
    res = preflight(client, "https://evil.example.test")
    assert "access-control-allow-origin" not in res.headers


def test_localhost_not_allowed_in_production():
    client = app_with(ENVIRONMENT="production", FRONTEND_HOST="https://app.example.test")
    res = preflight(client, "http://localhost:3000")
    assert "access-control-allow-origin" not in res.headers


def test_local_dev_origins_allowed_in_local():
    client = app_with(ENVIRONMENT="local", FRONTEND_HOST="https://app.example.test")
    for origin in ("http://localhost:3000", "http://127.0.0.1:3000"):
        assert preflight(client, origin).headers.get("access-control-allow-origin") == origin
