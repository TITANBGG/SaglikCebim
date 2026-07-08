from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Database URL
DATABASE_URL = "sqlite:///./dev.db"  # SQLite fallback
ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./dev.db"  # Async version for SQLite

# Sync engine & session
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine & session
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite+aiosqlite" in ASYNC_DATABASE_URL else {}
)

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Base for models
class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Dependency for getting async database session"""
    async with AsyncSessionLocal() as db:
        yield db


def init_db():
    """Initialize database and create tables"""
    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_schema_compatibility()


def _ensure_sqlite_schema_compatibility():
    """Small SQLite compatibility migrations for demo/local databases."""
    if not DATABASE_URL.startswith("sqlite"):
        return

    with engine.begin() as conn:
        columns = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(patient_medications)")).fetchall()
        }
        if columns:
            if "dosage" not in columns:
                conn.execute(text("ALTER TABLE patient_medications ADD COLUMN dosage VARCHAR(255)"))
            if "start_date" not in columns:
                conn.execute(text("ALTER TABLE patient_medications ADD COLUMN start_date VARCHAR(50)"))
