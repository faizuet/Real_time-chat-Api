from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID

from app.models.room_participant import RoomParticipant
from app.models.chat_room import ChatRoom
from app.models.user import User
from app.schemas.room_participant import (
    RoomParticipantCreate,
    RoomParticipantResponse,
)
from app.core.database import get_async_db
from app.core.security import get_current_user

router = APIRouter(prefix="/participants", tags=["Room Participants"])


# ------------------ Join a Chat Room ------------------
@router.post("/", response_model=RoomParticipantResponse, status_code=status.HTTP_201_CREATED)
async def join_chat_room(
    data: RoomParticipantCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Join a chat room."""
    try:
        room_uuid = UUID(data.room_id)
        user_uuid = UUID(data.user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    # Validate user
    if user_uuid != current_user.id:
        raise HTTPException(status_code=403, detail="You can only join as yourself")

    # Check if room exists
    room = await db.get(ChatRoom, room_uuid)
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    # Check if already a participant
    result = await db.execute(
        select(RoomParticipant).where(
            RoomParticipant.room_id == room_uuid, RoomParticipant.user_id == current_user.id
        )
    )
    existing_participant = result.scalar_one_or_none()
    if existing_participant:
        raise HTTPException(status_code=400, detail="You are already in this room")

    # Add participant
    participant = RoomParticipant(room_id=room_uuid, user_id=current_user.id)
    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    return participant


# ------------------ Get Room Participants ------------------
@router.get("/room/{room_id}", response_model=list[RoomParticipantResponse])
async def get_room_participants(
    room_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Get all participants in a specific chat room."""
    try:
        room_uuid = UUID(room_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid room ID format")

    room = await db.get(ChatRoom, room_uuid)
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    result = await db.execute(select(RoomParticipant).where(RoomParticipant.room_id == room_uuid))
    participants = result.scalars().all()
    return participants


# ------------------ Leave Chat Room ------------------
@router.delete("/{room_id}", status_code=status.HTTP_200_OK)
async def leave_chat_room(
    room_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Leave a chat room."""
    try:
        room_uuid = UUID(room_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid room ID format")

    result = await db.execute(
        select(RoomParticipant).where(
            RoomParticipant.room_id == room_uuid, RoomParticipant.user_id == current_user.id
        )
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise HTTPException(status_code=404, detail="You are not a member of this room")

    await db.execute(delete(RoomParticipant).where(RoomParticipant.id == participant.id))
    await db.commit()

    return {"detail": "Left chat room successfully"}

