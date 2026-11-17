"""Real-time collaborative editing over the Yjs sync protocol.

One in-process ``pycrdt`` WebsocketServer holds a room per document (room name =
file id). Rooms are created here, not by the server, so that each document's
saved state can be loaded before the first client syncs. Each room has a
persister that writes the full Yjs state to ``file.yjs_state`` at most every
``SAVE_INTERVAL`` seconds while it is being edited, and again when the last
client leaves or the app shuts down.

Rooms live in this process's memory, so the backend must run as a single
worker (see the Dockerfiles).
"""

from __future__ import annotations

import logging
import uuid
from contextlib import AsyncExitStack

import anyio
from anyio import to_thread
from anyio.abc import TaskGroup
from pycrdt import Doc
from pycrdt.websocket import WebsocketServer, YRoom, exception_logger
from sqlmodel import Session
from starlette.websockets import WebSocket

from app.core.db import engine
from app.models import File

log = logging.getLogger(__name__)

SAVE_INTERVAL = 2.0  # seconds


def session_factory() -> Session:
    """Open a DB session. Replaced in tests."""
    return Session(engine)


def _load_state(file_id: str) -> bytes | None:
    with session_factory() as session:
        file = session.get(File, uuid.UUID(file_id))
        return file.yjs_state if file else None


def _save_state(file_id: str, state: bytes) -> None:
    with session_factory() as session:
        file = session.get(File, uuid.UUID(file_id))
        if file is None:  # deleted while being edited
            return
        file.yjs_state = state
        session.add(file)
        session.commit()


class StarletteChannel:
    """Adapts a Starlette WebSocket to the pycrdt ``Channel`` protocol."""

    def __init__(self, websocket: WebSocket, path: str) -> None:
        self._websocket = websocket
        self._path = path
        self._send_lock = anyio.Lock()

    @property
    def path(self) -> str:
        return self._path

    def __aiter__(self) -> StarletteChannel:
        return self

    async def __anext__(self) -> bytes:
        try:
            return await self.recv()
        except Exception:  # disconnect or non-binary frame ends the session
            raise StopAsyncIteration()

    async def send(self, message: bytes) -> None:
        async with self._send_lock:
            await self._websocket.send_bytes(message)

    async def recv(self) -> bytes:
        return bytes(await self._websocket.receive_bytes())


class RoomPersister:
    """Saves a room's document while it changes (throttled) and on demand."""

    def __init__(self, file_id: str, ydoc: Doc, interval: float) -> None:
        self.file_id = file_id
        self.ydoc = ydoc
        self.interval = interval
        self._dirty = False
        self._changed = anyio.Event()
        self._save_lock = anyio.Lock()
        self._scope: anyio.CancelScope | None = None
        self._subscription = ydoc.observe(self._on_change)

    def _on_change(self, _event: object) -> None:
        self._dirty = True
        self._changed.set()

    async def run(self) -> None:
        with anyio.CancelScope() as scope:
            self._scope = scope
            while True:
                await self._changed.wait()
                self._changed = anyio.Event()
                await anyio.sleep(self.interval)
                await self.flush()

    async def flush(self) -> None:
        async with self._save_lock:
            if not self._dirty:
                return
            self._dirty = False
            state = self.ydoc.get_update()
            try:
                await to_thread.run_sync(_save_state, self.file_id, state)
            except Exception:
                self._dirty = True  # retry on the next change or close
                log.exception("Failed to save collaborative state for %s", self.file_id)

    async def close(self) -> None:
        if self._scope is not None:
            self._scope.cancel()
        await self.flush()
        self.ydoc.unobserve(self._subscription)


class CollabService:
    def __init__(self, save_interval: float = SAVE_INTERVAL) -> None:
        self.save_interval = save_interval
        self.server: WebsocketServer | None = None
        self._persisters: dict[str, RoomPersister] = {}
        self._rooms_lock = anyio.Lock()
        self._task_group: TaskGroup | None = None
        self._exit_stack: AsyncExitStack | None = None

    async def __aenter__(self) -> CollabService:
        if self.server is not None:
            raise RuntimeError("CollabService is already running")
        self.server = WebsocketServer(
            auto_clean_rooms=False, exception_handler=exception_logger, log=log
        )
        self._persisters = {}
        self._rooms_lock = anyio.Lock()
        async with AsyncExitStack() as stack:
            await stack.enter_async_context(self.server)
            self._task_group = await stack.enter_async_context(anyio.create_task_group())
            self._exit_stack = stack.pop_all()
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        async with self._rooms_lock:
            for file_id in list(self._persisters):
                await self._close_room(file_id)
        assert self._task_group is not None and self._exit_stack is not None
        self._task_group.cancel_scope.cancel()
        await self._exit_stack.aclose()
        self._task_group = None
        self.server = None

    async def _open_room(self, file_id: str) -> None:
        assert self.server is not None and self._task_group is not None
        if file_id in self.server.rooms:
            return
        ydoc = Doc()
        state = await to_thread.run_sync(_load_state, file_id)
        if state:
            ydoc.apply_update(state)
        room = YRoom(ready=True, ydoc=ydoc, exception_handler=exception_logger, log=log)
        self.server.rooms[file_id] = room
        await self.server.start_room(room)
        persister = RoomPersister(file_id, ydoc, self.save_interval)
        self._persisters[file_id] = persister
        self._task_group.start_soon(persister.run)

    async def _close_room(self, file_id: str) -> None:
        assert self.server is not None
        persister = self._persisters.pop(file_id, None)
        if persister is not None:
            await persister.close()
        if file_id in self.server.rooms:
            await self.server.delete_room(name=file_id)

    async def serve(self, websocket: WebSocket, file_id: str) -> None:
        """Serve an already-accepted, already-authorized WebSocket for ``file_id``."""
        if self.server is None:
            raise RuntimeError("CollabService is not running")
        async with self._rooms_lock:
            await self._open_room(file_id)
        try:
            await self.server.serve(StarletteChannel(websocket, file_id))
        finally:
            async with self._rooms_lock:
                room = self.server.rooms.get(file_id) if self.server else None
                if room is not None and not room.clients:
                    await self._close_room(file_id)


collab_service = CollabService()
