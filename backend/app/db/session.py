from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

# Create asynchronous engine. For SQLite, we enforce single-threaded check bypass for compatibility
connect_args = {"check_same_thread": False} if "sqlite" in settings.DB_SCHEME else {}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    """Declarative base class for all system database models."""
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection provider for FastAPI routing contexts."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
