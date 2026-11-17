"""Registration and login."""

from .conftest import auth_header


def signup(client, email="new@example.com", password="correct-horse-1"):
    return client.post(
        "/api/v1/users/signup",
        json={"email": email, "password": password, "full_name": "New User"},
    )


def login(client, email, password):
    return client.post(
        "/api/v1/login/access-token", data={"username": email, "password": password}
    )


def test_signup_then_login_and_me(client):
    res = signup(client)
    assert res.status_code == 200
    assert res.json()["email"] == "new@example.com"
    assert "hashed_password" not in res.json()

    token_res = login(client, "new@example.com", "correct-horse-1")
    assert token_res.status_code == 200
    token = token_res.json()["access_token"]

    me = client.get("/api/v1/users/me", headers=auth_header(token))
    assert me.status_code == 200
    assert me.json()["full_name"] == "New User"


def test_duplicate_signup_rejected(client):
    assert signup(client).status_code == 200
    assert signup(client).status_code == 400


def test_wrong_password_rejected(client):
    signup(client)
    res = login(client, "new@example.com", "wrong-password")
    assert res.status_code == 400
    assert "access_token" not in res.json()


def test_unknown_user_rejected(client):
    assert login(client, "nobody@example.com", "whatever-123").status_code == 400


def test_me_requires_token(client):
    assert client.get("/api/v1/users/me").status_code == 401


def test_me_rejects_garbage_token(client):
    res = client.get("/api/v1/users/me", headers=auth_header("not-a-jwt"))
    assert res.status_code == 403
