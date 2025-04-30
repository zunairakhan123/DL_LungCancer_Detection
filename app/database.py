import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlmodel import SQLModel
from typing import Generator

# Load database credentials from environment variables
DATABASE_URL = "postgresql://postgres:zunaira@localhost/FYP_Cancer_db"

# Create a database engine
engine = create_engine(DATABASE_URL)

# Create a session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for getting the session
def get_session() -> Generator[Session, None, None]:
    """Yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create the database tables if they don't exist
def create_db_and_tables():
    SQLModel.metadata.create_all(bind=engine)
