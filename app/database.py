import sqlite3
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import DATABASE_URL

sqlite3.register_adapter(datetime, lambda dt: dt.isoformat(" "))

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _connection_record):
    """Enable FK enforcement on every new SQLite connection.

    Without this, ON DELETE CASCADE silently does nothing in SQLite.
    """
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: yields a DB session, always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
