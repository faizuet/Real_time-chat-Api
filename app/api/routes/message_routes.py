from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID

from app.models.message import Message
from app.models.chat_room import ChatRoom
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse
from app.core.database import get_async_db
from app.core.security import get_current_user

router = APIRouter(prefix="/messages", tags=["Messages"])


# ------------------ Create Message ------------------
@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Send a new message in a chat room."""
    # Validate UUIDs
    try:
        room_uuid = UUID(message_data.room_id)
        sender_uuid = UUID(message_data.sender_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    # Verify room exists
    room = await db.get(ChatRoom, room_uuid)
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    # Verify sender matches the authenticated user
    if sender_uuid != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to send as another user")

    # Create message
    new_message = Message(
        content=message_data.content,
        room_id=room_uuid,
        sender_id=current_user.id,
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message


# ------------------ Get Messages by Room ------------------
@router.get("/room/{room_id}", response_model=list[MessageResponse])
async def get_messages_by_room(
    room_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Get all messages from a chat room."""
    try:
        room_uuid = UUID(room_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid room ID format")

    # Check room exists
    room = await db.get(ChatRoom, room_uuid)
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    result = await db.execute(
        select(Message)
        .where(Message.room_id == room_uuid)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    return messages


# ------------------ Delete Message ------------------
@router.delete("/{message_id}", status_code=status.HTTP_200_OK)
async def delete_message(
    message_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a message (only sender can delete their own)."""
    try:
        message_uuid = UUID(message_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid message ID format")

    message = await db.get(Message, message_uuid)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own messages")

    await db.execute(delete(Message).where(Message.id == message_uuid))
    await db.commit()

    return {"detail": "Message deleted successfully"}

