from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import AuthResponse, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.core.database import get_async_db

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------- Register ----------------
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_async_db)):
    # Check if user already exists
    result = await db.execute(
        select(User).where(
            (User.username == user_data.username.strip()) |
            (User.email == user_data.email.lower())
        )
    )
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    # Hash password safely
    hashed_pw = hash_password(user_data.password)

    new_user = User(
        username=user_data.username.strip(),
        email=user_data.email.lower(),
        hashed_password=hashed_pw,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Convert UUID to string for Pydantic response
    return UserResponse(
        id=str(new_user.id),
        username=new_user.username,
        email=new_user.email,
        created_at=new_user.created_at
    )


# ---------------- Login ----------------
@router.post("/login", response_model=AuthResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
):
    # Fetch user from DB
    result = await db.execute(select(User).where(User.username == form_data.username.strip()))
    user = result.scalars().first()

    # Verify password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    return AuthResponse(
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at
        ),
        token=Token(access_token=access_token)
    )

