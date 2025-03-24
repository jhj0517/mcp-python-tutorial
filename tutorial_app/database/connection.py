from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from contextlib import contextmanager
from .models import Base

engine = create_engine("sqlite:///tutorial.db", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_engine = create_async_engine("sqlite+aiosqlite:///tutorial.db", echo=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db_session():
    """Get a database session with context management for automatic closing"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db_session():
    """Get an async database session"""
    async with AsyncSessionLocal() as session:
        yield session 