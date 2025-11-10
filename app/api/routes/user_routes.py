from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
from uuid import UUID

from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.core.database import get_async_db
from app.core.security import get_current_user, hash_password

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id != current_user.id))
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_async_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    user_data = user_update.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = hash_password(user_data.pop("password"))
    stmt = (
        update(User)
        .where(User.id == current_user.id)
        .values(**user_data)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()
    return await db.get(User, current_user.id)

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(delete(User).where(User.id == current_user.id))
    await db.commit()

