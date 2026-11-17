"""Collaborative state is saved and restored (specs/realtime-collaboration)."""

import time

from pycrdt import Doc, Text, YMessageType, YSyncMessageType, create_sync_message, create_update_message, handle_sync_message

from app.models import File
from app.services.collab import collab_service


def url(file, token: str) -> str:
    return f"/api/v1/collab/{file.id}?token={token}"


def write_text(ws, text: str) -> None:
    """Act as a y-websocket client that types `text` into the shared 'quill' text."""
    ws.receive_bytes()  # server's sync step 1
    doc = Doc()
    doc["quill"] = ytext = Text()
    ytext += text
    ws.send_bytes(create_update_message(doc.get_update()))


def read_text(ws) -> str:
    """Sync an empty client doc from the server and return the shared text."""
    doc = Doc()
    doc["quill"] = ytext = Text()
    ws.receive_bytes()  # server's sync step 1
    ws.send_bytes(create_sync_message(doc))  # our step 1 -> server replies with step 2
    while True:
        message = ws.receive_bytes()
        if message[0] == YMessageType.SYNC and message[1] == YSyncMessageType.SYNC_STEP2:
            handle_sync_message(message[1:], doc)
            return str(ytext)


def stored_state(session, file) -> bytes | None:
    session.expire_all()
    return session.get(File, file.id).yjs_state


def wait_for(predicate, timeout: float = 3.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.05)
    return False


def test_state_saved_on_last_disconnect_and_restored(client, session, file_of_a, user_a, access_token):
    token = access_token(user_a)
    with client.websocket_connect(url(file_of_a, token)) as ws:
        write_text(ws, "hello from client 1")

    assert wait_for(lambda: stored_state(session, file_of_a) is not None)

    with client.websocket_connect(url(file_of_a, token)) as ws:
        assert read_text(ws) == "hello from client 1"


def test_state_saved_while_editing_and_survives_restart(
    app_client, session, file_of_a, user_a, access_token, monkeypatch
):
    monkeypatch.setattr(collab_service, "save_interval", 0.1)
    token = access_token(user_a)
    with app_client() as first_run:
        with first_run.websocket_connect(url(file_of_a, token)) as ws:
            write_text(ws, "saved without disconnecting")
            # Saved by the periodic persister while the client is still connected.
            assert wait_for(lambda: stored_state(session, file_of_a) is not None)

    # Restart: a fresh app lifespan starts with no rooms in memory.
    with app_client() as second_run:
        with second_run.websocket_connect(url(file_of_a, token)) as ws:
            assert read_text(ws) == "saved without disconnecting"


def test_two_clients_see_each_others_edits(client, file_of_a, user_a, access_token, share_token):
    with client.websocket_connect(url(file_of_a, access_token(user_a))) as owner:
        write_text(owner, "from owner")
        with client.websocket_connect(
            f"/api/v1/collab/{file_of_a.id}?share_token={share_token(file_of_a.id)}"
        ) as guest:
            assert read_text(guest) == "from owner"
