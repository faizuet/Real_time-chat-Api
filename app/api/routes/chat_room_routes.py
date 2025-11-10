from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from uuid import UUID

from app.models.chat_room import ChatRoom
from app.models.user import User
from app.schemas.chat_room import ChatRoomCreate, ChatRoomUpdate, ChatRoomResponse
from app.core.database import get_async_db
from app.core.security import get_current_user

router = APIRouter(prefix="/chat-rooms", tags=["Chat Rooms"])


# ------------------ Create Chat Room ------------------
@router.post("/", response_model=ChatRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_room(
    room_data: ChatRoomCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new chat room."""
    new_room = ChatRoom(
        name=room_data.name,
        created_by=current_user.id,
        is_private=room_data.is_private,
    )
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    return new_room


# ------------------ Get All Chat Rooms ------------------
@router.get("/", response_model=list[ChatRoomResponse])
async def get_all_chat_rooms(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Get all chat rooms."""
    result = await db.execute(select(ChatRoom))
    rooms = result.scalars().all()
    return rooms


# ------------------ Get Chat Room by ID ------------------
@router.get("/{room_id}", response_model=ChatRoomResponse)
async def get_chat_room_by_id(
    room_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Get chat room details by ID."""
    try:
        room_uuid = UUID(room_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid room ID format")

    room = await db.get(ChatRoom, room_uuid)
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    return room


# ------------------ Update Chat Room ------------------
@router.put("/{room_id}", response_model=ChatRoomResponse)
async def update_chat_room(
    room_id: str,
    room_update: ChatRoomUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update chat room details (only by creator)."""
    try:
        room_uuid = UUID(room_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid room ID format")

    room = await db.get(ChatRoom, room_uuid)
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    if room.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this room")

    update_data = room_update.model_dump(exclude_unset=True)
    stmt = (
        update(ChatRoom)
        .where(ChatRoom.id == room_uuid)
        .values(**update_data)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()
    updated_room = await db.get(ChatRoom, room_uuid)
    return updated_room


@router.delete("/{room_id}", status_code=status.HTTP_200_OK)
async def delete_chat_room(
    room_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a chat room (only by creator)."""
    try:
        room_uuid = UUID(room_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid room ID format")

    room = await db.get(ChatRoom, room_uuid)
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")

    if room.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this room")

    await db.execute(delete(ChatRoom).where(ChatRoom.id == room_uuid))
    await db.commit()
    return {"detail": "Chat room deleted successfully"}

