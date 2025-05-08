from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import geoalchemy2

# Create async engine for PostgreSQL with PostGIS
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.debug,
    future=True,
)

# Create sync engine for migrations and other sync operations
sync_engine = create_engine(
    str(settings.DATABASE_URL).replace("+asyncpg", ""),
    echo=settings.debug,
    future=True,
)

# Base class for SQLAlchemy models
Base = declarative_base()

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

async def get_db() -> AsyncSession:
    """
    Dependency for getting async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Initialize PostGIS extension if it doesn't exist
async def init_db():
    """
    Initialize database with PostGIS extension
    """
    # This needs to be run with sync engine as extensions are typically created in sync mode
    with sync_engine.begin() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS postgis;")