from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    # ---------- Columns ----------
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ---------- Relationships ----------
    messages = relationship("Message", back_populates="sender", cascade="all, delete-orphan")
    chat_rooms = relationship("ChatRoom", back_populates="creator", cascade="all, delete-orphan")
    connections = relationship("ActiveConnection", back_populates="user", cascade="all, delete-orphan")
    participating_rooms = relationship("RoomParticipant", back_populates="user", cascade="all, delete")

