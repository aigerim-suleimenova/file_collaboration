"""The old unauthenticated collaboration endpoints must not exist (specs/realtime-collaboration)."""

import uuid

import pytest
from starlette.websockets import WebSocketDisconnect


def test_broadcast_endpoint_removed(client):
    res = client.post(f"/api/v1/file/{uuid.uuid4()}/broadcast", json={"type": "x"})
    assert res.status_code == 404


def test_users_endpoint_removed(client):
    res = client.get(f"/api/v1/file/{uuid.uuid4()}/users")
    assert res.status_code == 404


def test_legacy_websocket_not_accepted(client, user_a, access_token):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            f"/api/v1/ws/{uuid.uuid4()}?token={access_token(user_a)}"
        ) as ws:
            ws.receive_text()
