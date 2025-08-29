import asyncio
import json
from typing import Dict, List, Any

from fastapi import WebSocket


class FileConnectionManager:
    def __init__(self) -> None:
        # Track connections per file: {file_id: [websocket_connections]}
        self.file_connections: Dict[str, List[WebSocket]
                                    ] = Dict[str, List[WebSocket]]()
        # Track user info per connection: {websocket: {"user_id": str, "file_id": str}}
        self.connection_info: Dict[WebSocket,
                                   Dict[str, str]] = Dict[WebSocket, Dict[str, str]]()

    async def connect_to_file(self, websocket: WebSocket, file_id: str, user_id: str) -> None:
        """Connect a user to a specific file for collaboration"""
        await websocket.accept()

        if file_id not in self.file_connections:
            self.file_connections[file_id] = []

        self.file_connections[file_id].append(websocket)
        self.connection_info[websocket] = {
            "user_id": user_id, "file_id": file_id}

        # Notify other users that someone joined this file
        await self.broadcast_to_file(
            file_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "file_id": file_id,
                "timestamp": asyncio.get_running_loop().time(),
            },
            exclude_websocket=websocket,
        )

        # Send confirmation to the user who just connected
        await websocket.send_text(
            json.dumps(
                {
                    "type": "connected",
                    "message": f"Connected to file {file_id}",
                    "file_id": file_id,
                    "user_id": user_id,
                }
            )
        )

    def disconnect_from_file(self, websocket: WebSocket) -> None:
        """Disconnect a user from a file"""
        if websocket in self.connection_info:
            info = self.connection_info[websocket]
            file_id = info["file_id"]
            user_id = info["user_id"]

            # Remove from file connections
            if file_id in self.file_connections:
                self.file_connections[file_id].remove(websocket)
                if not self.file_connections[file_id]:
                    del self.file_connections[file_id]

            # Remove connection info
            del self.connection_info[websocket]

            # Notify other users that someone left
            asyncio.create_task(
                self.broadcast_to_file(
                    file_id,
                    {
                        "type": "user_left",
                        "user_id": user_id,
                        "file_id": file_id,
                        "timestamp": asyncio.get_running_loop().time(),
                    },
                )
            )

    async def broadcast_to_file(
        self, file_id: str, message: dict[str, Any], exclude_websocket: WebSocket | None = None
    ) -> None:
        """Send message to all users connected to a specific file"""
        if file_id in self.file_connections:
            for connection in self.file_connections[file_id]:
                if connection != exclude_websocket:
                    try:
                        await connection.send_text(json.dumps(message))
                    except Exception as e:
                        # Remove broken connection
                        print(f"Error broadcasting to connection: {e}")
                        self.disconnect_from_file(connection)

    async def send_to_user(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        """Send message to a specific user"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending to user: {e}")
            # Connection is broken, disconnect
            if websocket in self.connection_info:
                self.disconnect_from_file(websocket)

    def get_file_users(self, file_id: str) -> list[str]:
        """Get list of user IDs currently editing a file"""
        if file_id in self.file_connections:
            return [
                self.connection_info[conn]["user_id"]
                for conn in self.file_connections[file_id]
            ]
        return []

    async def handle_file_message(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        """Handle incoming messages from file collaborators"""
        try:
            message_type = message.get("type")

            if message_type == "file_update":
                # Broadcast file changes to other users
                if websocket in self.connection_info:
                    file_id = self.connection_info[websocket]["file_id"]
                    await self.broadcast_to_file(
                        file_id, message, exclude_websocket=websocket
                    )

            elif message_type == "cursor_move":
                # Broadcast cursor position updates
                if websocket in self.connection_info:
                    file_id = self.connection_info[websocket]["file_id"]
                    await self.broadcast_to_file(
                        file_id, message, exclude_websocket=websocket
                    )

            elif message_type == "ping":
                # Respond to ping with pong
                await self.send_to_user(websocket, {"type": "pong"})

        except Exception as e:
            print(f"Error handling file message: {e}")
            await self.send_to_user(
                websocket, {"type": "error",
                            "message": "Failed to process message"}
            )
