import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..deps import FileManagerDep, decode_access_token
from typing import Any

router = APIRouter()


@router.websocket("/ws/{file_id}")
async def websocket_endpoint(
    websocket: WebSocket, file_id: str, manager: FileManagerDep
) -> None:
    """
    WebSocket endpoint for real-time file collaboration.
    Users can connect to edit files together in real-time.
    """
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            return

        # Decode and validate token
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            if not user_id:
                await websocket.close(code=4001, reason="Invalid token payload")
                return
        except Exception:
            await websocket.close(code=4001, reason="Invalid authentication token")
            return

        # Connect user to file
        await manager.connect_to_file(websocket, file_id, user_id)

        try:
            # Handle incoming messages
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Process the message
                await manager.handle_file_message(websocket, message)

        except WebSocketDisconnect:
            # User disconnected
            manager.disconnect_from_file(websocket)

    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass


@router.get("/file/{file_id}/users")
async def get_file_users(file_id: str, manager: FileManagerDep) -> dict[str, str | list[str]]:
    users = manager.get_file_users(file_id)
    return {"file_id": file_id, "users": users}


@router.post("/file/{file_id}/broadcast")
async def broadcast_to_file(file_id: str, message: dict[str, Any], manager: FileManagerDep) -> dict[str, str]:
    await manager.broadcast_to_file(file_id, message)
    return {"message": "Broadcast sent", "file_id": file_id}
