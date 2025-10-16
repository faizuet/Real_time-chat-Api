from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class RoomParticipant(Base):
    __tablename__ = "room_participants"

    # ---------- Columns ----------
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_rooms.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---------- Relationships ----------
    room = relationship("ChatRoom", back_populates="participants")
    user = relationship("User", back_populates="participating_rooms")

    # ---------- Constraints ----------
    __table_args__ = (
        UniqueConstraint("room_id", "user_id", name="unique_room_user"),
    )

