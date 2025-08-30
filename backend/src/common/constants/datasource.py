"""Database datasource configuration constants."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Generator
from ..config import config

# Database URL construction
DATABASE_URL = (
    f"postgresql://{config.db_username}:{config.db_password}@"
    f"{config.db_host}:{config.db_port}/{config.db_database}"
)

# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, pool_pre_ping=True, pool_recycle=300, echo=config.debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


@contextmanager
def get_db_session() -> Generator:
    """Database session context manager."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    """Dependency injection function for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database connection constants
class DatabaseConstants:
    """Database related constants."""

    MAX_CONNECTIONS = 20
    MIN_CONNECTIONS = 5
    CONNECTION_TIMEOUT = 30
    QUERY_TIMEOUT = 60

    # Migration paths
    MIGRATIONS_PATH = "src/db/migrations"

    # Entity imports (to be added as needed)
    ENTITIES = [
        # Add entity classes here as they are created
    ]
