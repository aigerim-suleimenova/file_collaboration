from app.core.security import ALGORITHM
from app.core.config import settings
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from sqlmodel import Session

from app import crud
from app.api.deps import get_db
from app.api.routes import login, users, websocket
from app.api.routes import files

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(files.router, prefix="/files")
api_router.include_router(websocket.router)


@api_router.get("/public/files/{file_id}")
def get_public_file(file_id: uuid.UUID, token: str, session: Session = Depends(get_db)) -> dict[str, Any]:
    """Read-only public access via short-lived share token bound to file_id."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

    # Accept either explicit file_id claim (new tokens) or legacy sub JSON
    file_id_claim = payload.get("file_id")
    if not file_id_claim and isinstance(payload.get("sub"), str):
        try:
            import json as _json
            if payload["sub"].startswith("{"):
                sub_obj = _json.loads(payload["sub"])  # legacy encoded
                file_id_claim = sub_obj.get("file_id")
        except Exception:
            file_id_claim = None

    if file_id_claim != str(file_id):
        raise HTTPException(
            status_code=403, detail="Token does not grant access to this file"
        )

    file = crud.get_file_by_id(session, file_id=file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Return file data including content for editing
    return {
        "id": str(file.id),
        "filename": file.filename,
        "s3_key": file.s3_key,
        "file_size": file.file_size,
        "mime_type": file.mime_type,
        "original_format": file.original_format,
        "quill_content": file.quill_content,
        # Use quill_content if available, otherwise empty
        "content": file.quill_content or "",
        "owner_id": str(file.owner_id),
        "created_at": file.created_at.isoformat() if file.created_at else None,
        "updated_at": file.updated_at.isoformat() if file.updated_at else None,
    }
