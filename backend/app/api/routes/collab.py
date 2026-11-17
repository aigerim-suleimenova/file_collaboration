"""Authenticated Yjs collaboration endpoint: WS /api/v1/collab/{file_id}."""

import uuid
from typing import Any

from fastapi import APIRouter, WebSocket
from jose import JWTError, jwt
from sqlmodel import Session
from starlette.concurrency import run_in_threadpool

from app.api.deps import SessionDep
from app.core import security
from app.core.config import settings
from app.models import File, User
from app.services.collab import collab_service

router = APIRouter()

CLOSE_UNAUTHENTICATED = 4001  # missing, invalid or expired credentials
CLOSE_FORBIDDEN = 4003  # valid credentials without access to this file
CLOSE_NOT_FOUND = 4004  # file does not exist


def _decode(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        return None


def _parse_uuid(value: object) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(value))
    except ValueError:
        return None


def authorize(
    session: Session, file_id: str, token: str | None, share_token: str | None
) -> int | None:
    """Return a close code if the connection must be refused, else None."""
    owner_id: uuid.UUID | None = None
    shared_file_id: str | None = None

    if token:
        payload = _decode(token)
        user_id = _parse_uuid(payload.get("sub")) if payload else None
        user = session.get(User, user_id) if user_id else None
        if user is None or not user.is_active:
            return CLOSE_UNAUTHENTICATED
        owner_id = user.id
    elif share_token:
        payload = _decode(share_token)
        shared_file_id = payload.get("file_id") if payload else None
        if not shared_file_id:
            return CLOSE_UNAUTHENTICATED
    else:
        return CLOSE_UNAUTHENTICATED

    file_uuid = _parse_uuid(file_id)
    file = session.get(File, file_uuid) if file_uuid else None
    if file is None:
        return CLOSE_NOT_FOUND

    if owner_id is not None and file.owner_id != owner_id:
        return CLOSE_FORBIDDEN
    if shared_file_id is not None and shared_file_id != str(file.id):
        return CLOSE_FORBIDDEN
    return None


@router.websocket("/collab/{file_id}")
async def collaborate(websocket: WebSocket, file_id: str, session: SessionDep) -> None:
    params = websocket.query_params
    try:
        close_code = await run_in_threadpool(
            authorize, session, file_id, params.get("token"), params.get("share_token")
        )
    finally:
        # Don't hold a pooled DB connection for the lifetime of the socket.
        session.close()

    # Accept first so the browser can see the specific close code (a rejected
    # handshake only surfaces as 1006). No document data is sent before closing.
    await websocket.accept()
    if close_code is not None:
        await websocket.close(code=close_code)
        return

    await collab_service.serve(websocket, str(uuid.UUID(file_id)))
