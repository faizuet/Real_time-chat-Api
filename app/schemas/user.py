from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(UserBase):
    id: str  # keep string for response
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_obj(cls, obj):
        """
        Convert SQLAlchemy object to Pydantic response,
        converting UUID to string.
        """
        return cls(
            id=str(obj.id),
            username=obj.username,
            email=obj.email,
            created_at=obj.created_at
        )

