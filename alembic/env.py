from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.engine import Connection
from alembic import context

from app.core.config import settings
from app.core.database import Base

from app.models import (
    user,
    chat_room,
    message,
    connection,
    room_participant,
)

# ------------------------------
# Alembic Config Setup
# ------------------------------
config = context.config

# Use DATABASE_URI from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URI)

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata

# ------------------------------
# Offline Migrations
# ------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URI
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # detect column type changes automatically
    )

    with context.begin_transaction():
        context.run_migrations()

# ------------------------------
# Online Migrations
# ------------------------------
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with AsyncEngine."""
    connectable: AsyncEngine = create_async_engine(
        settings.DATABASE_URI,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

# ------------------------------
# Run Migrations
# ------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())

