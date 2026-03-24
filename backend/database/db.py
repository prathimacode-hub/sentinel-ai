from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# -----------------------------
# DATABASE CONFIG
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'sentinel.db')}"

# -----------------------------
# ENGINE
# -----------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite
    echo=False  # set True for SQL debug logs
)

# -----------------------------
# SESSION FACTORY
# -----------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -----------------------------
# BASE MODEL
# -----------------------------
Base = declarative_base()


# -----------------------------
# DB DEPENDENCY (FASTAPI)
# -----------------------------
def get_db():
    """
    FastAPI dependency for DB session
    Usage:
        db = next(get_db())
    OR
        Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print("❌ DB Error:", e)
        db.rollback()
        raise
    finally:
        db.close()


# -----------------------------
# INIT FUNCTION (OPTIONAL)
# -----------------------------
def init_db():
    """
    Call this once to create all tables
    """
    from database.models import Base  # lazy import
    Base.metadata.create_all(bind=engine)
