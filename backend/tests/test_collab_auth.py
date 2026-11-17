"""Authorization rules for the collaboration WebSocket (specs/realtime-collaboration)."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt
from starlette.websockets import WebSocketDisconnect

from app.core.security import ALGORITHM

YJS_MESSAGE_SYNC = 0


def collab_url(file_id: object, **params: str) -> str:
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"/api/v1/collab/{file_id}" + (f"?{query}" if query else "")


def assert_closed_with(client, url: str, code: int) -> None:
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(url) as ws:
            ws.receive_bytes()  # must not receive any document data
    assert exc.value.code == code


def assert_accepted_and_synced(client, url: str) -> None:
    with client.websocket_connect(url) as ws:
        first = ws.receive_bytes()
        assert first[0] == YJS_MESSAGE_SYNC


def test_no_credentials_closes_4001(client, file_of_a):
    assert_closed_with(client, collab_url(file_of_a.id), 4001)


def test_garbage_token_closes_4001(client, file_of_a):
    assert_closed_with(client, collab_url(file_of_a.id, token="not-a-jwt"), 4001)


def test_expired_access_token_closes_4001(client, file_of_a, user_a, access_token):
    token = access_token(user_a, expires=timedelta(minutes=-1))
    assert_closed_with(client, collab_url(file_of_a.id, token=token), 4001)


def test_bad_signature_closes_4001(client, file_of_a, user_a):
    forged = jwt.encode(
        {"sub": str(user_a.id), "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "some-other-secret",
        algorithm=ALGORITHM,
    )
    assert_closed_with(client, collab_url(file_of_a.id, token=forged), 4001)


def test_expired_share_token_closes_4001(client, file_of_a, share_token):
    token = share_token(file_of_a.id, expires=timedelta(minutes=-1))
    assert_closed_with(client, collab_url(file_of_a.id, share_token=token), 4001)


def test_access_token_for_unknown_user_closes_4001(client, file_of_a, access_token):
    class Ghost:
        id = uuid.uuid4()

    token = access_token(Ghost())
    assert_closed_with(client, collab_url(file_of_a.id, token=token), 4001)


def test_non_owner_closes_4003(client, file_of_a, user_b, access_token):
    assert_closed_with(client, collab_url(file_of_a.id, token=access_token(user_b)), 4003)


def test_share_token_for_other_file_closes_4003(client, file_of_a, share_token):
    token = share_token(uuid.uuid4())
    assert_closed_with(client, collab_url(file_of_a.id, share_token=token), 4003)


def test_unknown_file_closes_4004(client, user_a, access_token):
    assert_closed_with(client, collab_url(uuid.uuid4(), token=access_token(user_a)), 4004)


def test_malformed_file_id_closes_4004(client, user_a, access_token):
    assert_closed_with(client, collab_url("not-a-uuid", token=access_token(user_a)), 4004)


def test_owner_is_accepted_and_synced(client, file_of_a, user_a, access_token):
    assert_accepted_and_synced(client, collab_url(file_of_a.id, token=access_token(user_a)))


def test_matching_share_token_is_accepted_and_synced(client, file_of_a, share_token):
    token = share_token(file_of_a.id)
    assert_accepted_and_synced(client, collab_url(file_of_a.id, share_token=token))
