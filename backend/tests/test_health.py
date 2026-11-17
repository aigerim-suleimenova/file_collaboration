"""GET /health (specs/service-health)."""

import pytest
from sqlalchemy.exc import OperationalError

import app.main as main


@pytest.fixture()
def health_engine(engine, monkeypatch):
    monkeypatch.setattr(main, "engine", engine)
    return engine


def test_healthy(client, health_engine):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "database": "ok"}


def test_no_auth_needed(client, health_engine):
    res = client.get("/health")
    assert res.status_code not in (401, 403)


def test_database_down_returns_503_without_details(client, health_engine, monkeypatch):
    def broken_connect(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("password=hunter2 host=db"))

    monkeypatch.setattr(health_engine, "connect", broken_connect)
    res = client.get("/health")
    assert res.status_code == 503
    assert res.json() == {"status": "error", "database": "unavailable"}
    assert "hunter2" not in res.text
