from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLite database URL
DATABASE_URL = "sqlite:///./tax_advisor.db"

# Create the SQLAlchemy engine
# For SQLite, check_same_thread=False allows usage across threads (needed in FastAPI)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a configured "SessionLocal" class for database session handling
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models to inherit from
Base = declarative_base()
