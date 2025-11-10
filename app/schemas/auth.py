from pydantic import BaseModel
from app.schemas.user import UserResponse


# ---------- Token Schema ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Auth Response Schema ----------
class AuthResponse(BaseModel):
    user: UserResponse
    token: Token

    class Config:
        from_attributes = True

