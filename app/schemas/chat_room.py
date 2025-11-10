from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRoomBase(BaseModel):
    name: Optional[str] = None
    is_private: bool = True


class ChatRoomCreate(ChatRoomBase):
    pass


class ChatRoomUpdate(BaseModel):
    name: Optional[str] = None
    is_private: Optional[bool] = None


class ChatRoomResponse(ChatRoomBase):
    id: str
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

