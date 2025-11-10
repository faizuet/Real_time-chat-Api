from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ActiveConnectionBase(BaseModel):
    room_id: str
    user_id: str
    connection_id: str


class ActiveConnectionCreate(ActiveConnectionBase):
    pass


class ActiveConnectionResponse(ActiveConnectionBase):
    id: str
    connected_at: datetime

    class Config:
        from_attributes = True

