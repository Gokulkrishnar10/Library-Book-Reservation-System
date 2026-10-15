"""Shared pytest fixtures for the backend test suite.

Uses an in-memory SQLite database with StaticPool so each test session
gets a clean, isolated database with no file I/O.

The FK PRAGMA listener is attached to the in-memory engine so ON DELETE
CASCADE behaves correctly in tests (same as in production).
"""

import os
import sqlite3
from datetime import datetime
import pytest

# Ensure tests run in isolated mock mode with zero network delays
os.environ["TESTING"] = "true"
os.environ["ENABLE_LIVE_EMAIL"] = "false"
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

sqlite3.register_adapter(datetime, lambda dt: dt.isoformat(" "))

from app.app_factory import create_app
from app.database import Base, get_db


@pytest.fixture(scope="function")
def db():
    """Yield a fresh in-memory SQLite session for each test function."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Must attach the FK PRAGMA listener to the in-memory engine too
    @event.listens_for(engine, "connect")
    def set_fk(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def client(db):
    """Yield a TestClient whose DB dependency is replaced with the in-memory session."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
