import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_URL

logger = logging.getLogger(__name__)

engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    """Yield a database session and ensure it closes after use."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"DB session error: {e}")
        raise
    finally:
        db.close()