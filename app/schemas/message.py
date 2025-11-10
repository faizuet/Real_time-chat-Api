from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    room_id: str
    sender_id: str


class MessageResponse(MessageBase):
    id: str
    room_id: str
    sender_id: str
    created_at: datetime

    class Config:
        from_attributes = True

