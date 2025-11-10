import logging
from fastapi import (
    APIRouter, WebSocket, WebSocketDisconnect,
    Depends, status
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.models.chat_room import ChatRoom
from app.models.message import Message
from app.schemas.message import MessageResponse
from app.websockets.connection_manager import ConnectionManager


router = APIRouter(prefix="/ws", tags=["WebSocket"])
manager = ConnectionManager()
logger = logging.getLogger(__name__)


@router.websocket("/chat/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(get_current_user),
):
    """
    WebSocket endpoint for real-time chat.

    Features:
    - Verifies room and connects authenticated users.
    - Broadcasts messages & system events.
    - Sends recent chat history (last 20 messages).
    - Tracks and updates online users list in real time.
    """

    try:
        # Validate chat room
        room = await db.get(ChatRoom, room_id)
        if not room:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Register new connection
        await manager.connect(room_id, websocket, current_user.id, current_user.username)

        # Notify room about join
        join_message = {
            "type": "system",
            "content": f" {current_user.username} joined the chat.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await manager.broadcast(room_id, join_message)

        # Send updated online users list
        await manager.broadcast(room_id, {
            "type": "online_users",
            "users": manager.get_online_users(room_id)
        })

        # Send recent chat history
        result = await db.execute(
            select(Message)
            .where(Message.room_id == room_id)
            .order_by(Message.created_at.desc())
            .limit(20)
        )
        recent_messages = result.scalars().all()
        for msg in reversed(recent_messages):
            msg_data = MessageResponse.model_validate(msg).model_dump()
            await websocket.send_json({
                "type": "history",
                "message": msg_data
            })

        # Main message loop
        while True:
            try:
                data = await websocket.receive_text()
            except Exception:
                await websocket.send_json({
                    "type": "error",
                    "content": "Invalid message format. Please send text only."
                })
                continue

            text = data.strip()
            if not text:
                continue

            # Save message to DB
            new_message = Message(
                room_id=room_id,
                sender_id=current_user.id,
                content=text,
                created_at=datetime.now(timezone.utc),
            )
            db.add(new_message)
            await db.commit()
            await db.refresh(new_message)

            msg_response = MessageResponse.model_validate(new_message)
            message_data = {
                "type": "message",
                "sender": current_user.username,
                "content": msg_response.content,
                "timestamp": msg_response.created_at.isoformat(),
            }

            # Broadcast the new message
            await manager.broadcast(room_id, message_data)

    except WebSocketDisconnect:
        # Handle disconnection gracefully
        manager.disconnect(room_id, websocket)
        logger.info(f"{current_user.username} disconnected from room {room_id}")

        # Notify room
        await manager.broadcast(room_id, {
            "type": "system",
            "content": f" {current_user.username} left the chat.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Update online users list
        await manager.broadcast(room_id, {
            "type": "online_users",
            "users": manager.get_online_users(room_id)
        })

    except Exception as e:
        # Rollback DB and close socket on unexpected error
        await db.rollback()
        logger.exception(f"[WebSocket Error] Room {room_id}: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

