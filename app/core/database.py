from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# ---------- Base Model ----------
Base = declarative_base()

# ---------- Engine ----------
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=False,  # set True only for debugging
    future=True,
)

# ---------- Session ----------
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ---------- Dependency ----------
async def get_async_db() -> AsyncSession:
    """FastAPI dependency that provides an async DB session."""
    async with async_session_maker() as session:
        yield session

