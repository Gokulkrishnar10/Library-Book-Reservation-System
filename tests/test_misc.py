"""Miscellaneous tests: Timezone UTC 'Z' formatting, FK CASCADE, concurrency, OpenAPI."""

import concurrent.futures
from datetime import datetime, timezone
import pytest
from sqlalchemy import text
from starlette.testclient import TestClient

from app.app_factory import create_app
from app.database import Base, get_db


# ---------------------------------------------------------------------------
# Timezone Tests
# ---------------------------------------------------------------------------

class TestTimezones:
    def test_reservation_timestamps_are_utc_aware(self, client):
        b = client.post("/books/", json={"title": "TZ Book", "author": "TZ", "total_copies": 2}).json()
        r = client.post(f"/books/{b['id']}/reserve", json={"user_name": "tz_user"}).json()

        # Both reservation_date and expires_at should be parseable and UTC
        res_date = r["reservation_date"]
        exp_date = r["expires_at"]
        assert res_date.endswith("Z") or "+00:00" in res_date
        assert exp_date.endswith("Z") or "+00:00" in exp_date

        # Check detail endpoint as well
        detail = client.get(f"/books/{b['id']}").json()
        d_res = detail["reservations"][0]
        assert d_res["expires_at"].endswith("Z") or "+00:00" in d_res["expires_at"]


# ---------------------------------------------------------------------------
# FK Cascade Tests
# ---------------------------------------------------------------------------

class TestForeignKeyCascade:
    def test_deleting_book_deletes_associated_reservations(self, client, db):
        b = client.post("/books/", json={"title": "Cascade Book", "author": "Author", "total_copies": 2}).json()
        book_id = b["id"]
        client.post(f"/books/{book_id}/reserve", json={"user_name": "user1"})
        client.post(f"/books/{book_id}/reserve", json={"user_name": "user2"})

        # Confirm 2 reservations exist
        count = db.execute(text("SELECT COUNT(*) FROM reservations WHERE book_id = :bid"), {"bid": book_id}).fetchone()[0]
        assert count == 2

        # Delete the book directly from DB to test SQLite FK CASCADE
        db.execute(text("DELETE FROM books WHERE id = :bid"), {"bid": book_id})
        db.commit()

        # Cascade should have deleted reservations
        count_after = db.execute(text("SELECT COUNT(*) FROM reservations WHERE book_id = :bid"), {"bid": book_id}).fetchone()[0]
        assert count_after == 0


# ---------------------------------------------------------------------------
# OpenAPI & Docs Tests
# ---------------------------------------------------------------------------

class TestOpenApi:
    def test_openapi_json_structure(self, client):
        r = client.get("/openapi.json")
        assert r.status_code == 200
        data = r.json()
        assert data["info"]["title"] == "Library Reservation API"
        paths = data["paths"]
        assert "/books/" in paths
        assert "/books/{book_id}" in paths
        assert "/books/{book_id}/reserve" in paths
        assert "/reservations/{reservation_id}" in paths

    def test_swagger_docs_endpoint(self, client):
        r = client.get("/docs")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Concurrency Tests (Thread pool)
# ---------------------------------------------------------------------------

class TestConcurrency:
    def test_concurrent_reserves_do_not_overbook(self, tmp_path):
        """Simulate concurrent reservation requests on a book with limited copies."""
        db_file = tmp_path / "test_concurrent.db"
        from sqlalchemy import create_engine, event
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(
            f"sqlite:///{db_file}",
            connect_args={"check_same_thread": False, "timeout": 30},
        )

        @event.listens_for(engine, "connect")
        def set_fk(conn, _):
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA journal_mode=WAL")

        Base.metadata.create_all(engine)
        SessionLocalTest = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        def override_get_db():
            s = SessionLocalTest()
            try:
                yield s
            finally:
                s.close()

        app = create_app()
        app.dependency_overrides[get_db] = override_get_db

        # Create a book with 3 copies
        with TestClient(app) as test_c:
            b = test_c.post("/books/", json={"title": "Concurrent Book", "author": "Author", "total_copies": 3}).json()
        book_id = b["id"]

        def attempt_reserve(user_idx):
            with TestClient(app) as c:
                return c.post(f"/books/{book_id}/reserve", json={"user_name": f"user_{user_idx}"})

        # Launch 6 concurrent requests (total 3 copies)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(attempt_reserve, i) for i in range(6)]
            results = [f.result() for f in futures]

        status_codes = [r.status_code for r in results]
        successes = status_codes.count(201)
        conflicts = status_codes.count(409)

        assert successes == 3
        assert conflicts == 3

        with TestClient(app) as test_c:
            final_book = test_c.get(f"/books/{book_id}").json()
            assert final_book["available_copies"] == 0
            assert len(final_book["reservations"]) == 3

