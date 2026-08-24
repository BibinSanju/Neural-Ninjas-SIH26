import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

# Ensure the database file is stored in the Backend directory
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workbench.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# For SQLite, check_same_thread=False is needed when sharing connections across requests
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create the database tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get the DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
