from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    # ---------- Columns ----------
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = Column(String(100), nullable=True)

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    is_private = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ---------- Relationships ----------
    # User who created the room
    creator = relationship(
        "User",
        back_populates="chat_rooms"
    )

    # Messages inside this room
    messages = relationship(
        "Message",
        back_populates="room",
        cascade="all, delete-orphan"
    )

    # WebSocket active connections
    connections = relationship(
        "ActiveConnection",
        back_populates="room",
        cascade="all, delete-orphan"
    )

    # Users participating in this room
    participants = relationship(
        "RoomParticipant",
        back_populates="room",
        cascade="all, delete-orphan"
    )

