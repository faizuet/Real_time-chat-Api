from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RoomParticipantBase(BaseModel):
    room_id: str
    user_id: str


class RoomParticipantCreate(RoomParticipantBase):
    pass


class RoomParticipantResponse(RoomParticipantBase):
    id: str
    joined_at: datetime

    class Config:
        from_attributes = True

