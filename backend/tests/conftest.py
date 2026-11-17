"""Shared fixtures: in-memory SQLite database, API client, users, files and tokens."""

from collections.abc import Callable, Generator
from contextlib import AbstractContextManager
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_db
from app.core.security import create_access_token, create_share_token
from app.main import app
from app.models import File, User
from app.services import collab


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def session(engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture()
def app_client(engine, monkeypatch) -> Callable[[], AbstractContextManager[TestClient]]:
    """Factory for a TestClient whose app lifespan (startup/shutdown) can be run repeatedly."""

    def override_get_db() -> Generator[Session, None, None]:
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_db] = override_get_db
    # The collaboration service opens its own sessions to load/save document state.
    monkeypatch.setattr(collab, "session_factory", lambda: Session(engine))
    yield lambda: TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def client(app_client) -> Generator[TestClient, None, None]:
    with app_client() as c:
        yield c


def _make_user(session: Session, email: str, full_name: str | None) -> User:
    user = User(email=email, full_name=full_name, hashed_password="not-used")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture()
def user_a(session) -> User:
    return _make_user(session, "a@example.com", "Aigerim")


@pytest.fixture()
def user_b(session) -> User:
    return _make_user(session, "b@example.com", None)


@pytest.fixture()
def file_of_a(session, user_a) -> File:
    file = File(filename="notes.html", owner_id=user_a.id, quill_content="<p>Hi</p>")
    session.add(file)
    session.commit()
    session.refresh(file)
    return file


@pytest.fixture()
def access_token() -> Callable[..., str]:
    def make(user: User, expires: timedelta = timedelta(minutes=30)) -> str:
        return create_access_token(user.id, expires_delta=expires)

    return make


@pytest.fixture()
def share_token() -> Callable[..., str]:
    def make(file_id: object, expires: timedelta = timedelta(hours=1)) -> str:
        return create_share_token(str(file_id), expires_delta=expires)

    return make


class FakeS3:
    """In-memory stand-in for app.services.s3_service.s3_service (same method signatures)."""

    METHODS = ("upload_file", "download_file", "get_file_url", "delete_file")

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def upload_file(self, file_path: str, s3_key: str) -> bool:
        with open(file_path, "rb") as f:
            self.objects[s3_key] = f.read()
        return True

    def download_file(self, s3_key: str, local_path: str) -> bool:
        if s3_key not in self.objects:
            return False
        with open(local_path, "wb") as f:
            f.write(self.objects[s3_key])
        return True

    def get_file_url(self, s3_key: str, expires_in: int = 3600) -> str | None:
        return f"https://fake-s3.test/{s3_key}?expires={expires_in}" if s3_key in self.objects else None

    def delete_file(self, s3_key: str) -> bool:
        return self.objects.pop(s3_key, None) is not None


@pytest.fixture()
def fake_s3(monkeypatch) -> FakeS3:
    from app.services.s3_service import s3_service

    fake = FakeS3()
    for name in FakeS3.METHODS:
        monkeypatch.setattr(s3_service, name, getattr(fake, name))
    return fake


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
