from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


# ---------- Request Schemas ----------

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


# ---------- Response Schemas ----------

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

