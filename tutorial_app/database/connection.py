from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from contextlib import contextmanager
import os
from .models import Base

# Get the directory where the application is located
APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(APP_DIR, "tutorial.db")

# Use absolute path for database
engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}", echo=True)
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