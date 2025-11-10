from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# ---------- Base Model ----------
Base = declarative_base()

# ---------- Engine ----------
engine = create_async_engine(
    settings.DATABASE_URI,
    echo=False,
    future=True,
)

# ---------- Session Maker ----------
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ---------- Dependency ----------
async def get_async_db() -> AsyncSession:
    """
    FastAPI dependency that provides an async database session.
    Usage:
        async def endpoint(db: AsyncSession = Depends(get_async_db)):
            ...
    """
    async with async_session_maker() as session:
        yield session

