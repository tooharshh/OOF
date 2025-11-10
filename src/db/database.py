from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from src.core.config import settings

Base = declarative_base()

# Sync engine for migrations
engine = create_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Async engine for API
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://"),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
