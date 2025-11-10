from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class ActiveConnection(Base):
    __tablename__ = "active_connections"

    # ---------- Columns ----------
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    room_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_rooms.id", ondelete="CASCADE"),
        nullable=False
    )
    connected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---------- Relationships ----------
    user = relationship("User", back_populates="connections")
    room = relationship("ChatRoom", back_populates="connections")

