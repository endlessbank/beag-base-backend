from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings


def get_pg8000_database_url(database_url: str) -> str:
    """
    Convert postgresql:// URLs to postgresql+pg8000:// for pg8000 driver compatibility.
    This allows using standard Render Database URLs without manual modification.
    """
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+pg8000://", 1)
    return database_url


# Create engine for PostgreSQL with pg8000 driver
database_url = get_pg8000_database_url(settings.database_url)
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()