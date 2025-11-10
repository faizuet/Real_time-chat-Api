from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_async_db
from app.models.user import User

# ---------------- Password Handling ----------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_BCRYPT_LENGTH = 72  # bcrypt can handle up to 72 bytes

def hash_password(password: str) -> str:
    """
    Hash the password safely, truncating to 72 bytes for bcrypt.
    """
    safe_password = password.strip()[:MAX_BCRYPT_LENGTH]
    return pwd_context.hash(safe_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify the password safely, truncating to 72 bytes for bcrypt.
    """
    safe_password = plain_password.strip()[:MAX_BCRYPT_LENGTH]
    return pwd_context.verify(safe_password, hashed_password)


# ---------------- JWT Handling ----------------
def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[dict[str, str]]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
        return payload
    except JWTError:
        return None


# ---------------- OAuth2 ----------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise credentials_exception

    try:
        user_id = uuid.UUID(payload["sub"])
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise credentials_exception

    return user

