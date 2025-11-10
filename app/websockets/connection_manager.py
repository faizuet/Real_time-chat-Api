from typing import Dict, List, Any
from fastapi import WebSocket
from uuid import UUID
import json


class ConnectionManager:
    """
    Manages active WebSocket connections for all chat rooms.
    - Tracks connected users per room.
    - Supports personal messages, broadcasts, and user listing.
    """

    def __init__(self):
        # room_id -> list of { "websocket": WebSocket, "user_id": str, "username": str }
        self.active_connections: Dict[UUID, List[Dict[str, Any]]] = {}

    async def connect(self, room_id: UUID, websocket: WebSocket, user_id: str, username: str):
        """Accept and store a new connection for a user."""
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = []

        self.active_connections[room_id].append({
            "websocket": websocket,
            "user_id": user_id,
            "username": username,
        })

    def disconnect(self, room_id: UUID, websocket: WebSocket):
        """Remove a WebSocket connection when a user disconnects."""
        if room_id not in self.active_connections:
            return

        self.active_connections[room_id] = [
            conn for conn in self.active_connections[room_id]
            if conn["websocket"] != websocket
        ]

        if not self.active_connections[room_id]:
            del self.active_connections[room_id]


    @staticmethod
    async def send_personal_message(message: Any, websocket: WebSocket):
        """Send a message to a single WebSocket connection."""
        if isinstance(message, (dict, list)):
            await websocket.send_json(message)
        else:
            await websocket.send_text(str(message))

    async def broadcast(self, room_id: UUID, message: Any, exclude: WebSocket | None = None):
        """
        Broadcast a message to all users in the room.
        Optionally exclude a sender connection.
        """
        if room_id not in self.active_connections:
            return

        for conn in self.active_connections[room_id]:
            ws = conn["websocket"]
            if ws == exclude:
                continue
            try:
                if isinstance(message, (dict, list)):
                    await ws.send_json(message)
                else:
                    await ws.send_text(str(message))
            except Exception:
                pass

    def get_online_users(self, room_id: UUID) -> List[Dict[str, str]]:
        """Return a list of online users (id & username) in the room."""
        if room_id not in self.active_connections:
            return []
        return [
            {"user_id": conn["user_id"], "username": conn["username"]}
            for conn in self.active_connections[room_id]
        ]

    def get_room_count(self, room_id: UUID) -> int:
        """Return number of active connections in a room."""
        return len(self.active_connections.get(room_id, []))

