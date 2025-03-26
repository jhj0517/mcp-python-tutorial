from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from contextlib import contextmanager
import os
from .models import Base
from functools import wraps
import json

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

def db_operation(func):
    """AOP decorator for database operations - handles session creation, error handling, and JSON output"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = None
        try:
            # Create a new session if one isn't provided
            if 'session' not in kwargs:
                session = SessionLocal()
                kwargs['session'] = session
                
            # Execute the function
            result = func(*args, **kwargs)
            
            # Commit changes if we created the session
            if session:
                session.commit()
            
            # If the result is not already JSON formatted (a string starting with '{' or '[')
            if not isinstance(result, str) or not (result.strip().startswith('{') or result.strip().startswith('[')):
                # Handle raw Python types by wrapping in a success response
                if result is None:
                    return json.dumps({"success": True}, ensure_ascii=False)
                else:
                    return json.dumps({"success": True, "data": result}, ensure_ascii=False)
                
            return result
        except Exception as e:
            if session:
                session.rollback()
            return json.dumps({"error": str(e)}, ensure_ascii=False)
        finally:
            # Close session if we created it
            if session:
                session.close()
    return wrapper