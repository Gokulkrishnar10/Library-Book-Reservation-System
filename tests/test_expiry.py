"""Tests for lazy expiry logic and inventory invariant preservation."""

from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def create_book(client, title="Test Book", author="Test Author", total_copies=3):
    return client.post("/books/", json={
        "title": title,
        "author": author,
        "total_copies": total_copies,
    })


def insert_expired_reservation(db, book_id, user_name="expired_user", days_ago=2):
    """Manually insert an expired reservation and decrement available_copies to simulate past reservation."""
    past = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days_ago)
    res = db.execute(
        text("""
            INSERT INTO reservations (book_id, user_name, reservation_date, expires_at)
            VALUES (:bid, :user, :res_date, :exp)
        """),
        {"bid": book_id, "user": user_name, "res_date": past - timedelta(days=7), "exp": past},
    )
    db.execute(
        text("UPDATE books SET available_copies = available_copies - 1 WHERE id = :bid"),
        {"bid": book_id},
    )
    db.commit()


# ---------------------------------------------------------------------------
# Test Lazy Expiry
# ---------------------------------------------------------------------------

class TestExpiry:
    def test_expired_reservation_purged_on_get_book(self, client, db):
        b = create_book(client, total_copies=2).json()
        book_id = b["id"]

        # Insert expired reservation
        insert_expired_reservation(db, book_id, "past_user")

        # Before GET, direct DB query shows 1 available
        row = db.execute(text("SELECT available_copies FROM books WHERE id = :bid"), {"bid": book_id}).fetchone()
        assert row[0] == 1

        # GET /books/{id} triggers purge
        r = client.get(f"/books/{book_id}")
        assert r.status_code == 200
        body = r.json()
        assert body["available_copies"] == 2
        assert len(body["reservations"]) == 0

    def test_expired_reservation_purged_on_list_books(self, client, db):
        b = create_book(client, total_copies=1).json()
        book_id = b["id"]

        insert_expired_reservation(db, book_id, "past_user")

        # GET /books/ triggers purge
        r = client.get("/books/")
        assert r.status_code == 200
        books = r.json()
        book = next(bk for bk in books if bk["id"] == book_id)
        assert book["available_copies"] == 1

    def test_reserve_succeeds_when_only_expired_reservations_exist(self, client, db):
        b = create_book(client, total_copies=1).json()
        book_id = b["id"]

        # 1 copy total, occupied by expired reservation
        insert_expired_reservation(db, book_id, "past_user")

        # New reservation should succeed because expired is purged first
        r = client.post(f"/books/{book_id}/reserve", json={"user_name": "new_user"})
        assert r.status_code == 201

        b_check = client.get(f"/books/{book_id}").json()
        assert b_check["available_copies"] == 0
        assert len(b_check["reservations"]) == 1
        assert b_check["reservations"][0]["user_name"] == "new_user"

    def test_cancel_expired_reservation_returns_404_no_double_increment(self, client, db):
        b = create_book(client, total_copies=2).json()
        book_id = b["id"]

        past = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=2)
        cursor = db.execute(
            text("""
                INSERT INTO reservations (book_id, user_name, reservation_date, expires_at)
                VALUES (:bid, 'expired_guy', :res_date, :exp)
            """),
            {"bid": book_id, "res_date": past, "exp": past},
        )
        db.execute(text("UPDATE books SET available_copies = 1 WHERE id = :bid"), {"bid": book_id})
        db.commit()
        res_id = cursor.lastrowid

        # Calling DELETE /reservations/{id} purges expired first, so reservation is gone -> 404
        r = client.delete(f"/reservations/{res_id}")
        assert r.status_code == 404

        # available_copies is recomputed to 2 (total 2 - 0 active), not double incremented to 3
        b_check = client.get(f"/books/{book_id}").json()
        assert b_check["available_copies"] == 2

    def test_inventory_invariants_hold_with_mixed_active_and_expired(self, client, db):
        b = create_book(client, total_copies=3).json()
        book_id = b["id"]

        # 1 active reservation
        client.post(f"/books/{book_id}/reserve", json={"user_name": "active_user"})

        # 1 expired reservation
        insert_expired_reservation(db, book_id, "expired_user")

        # Check via GET
        b_after = client.get(f"/books/{book_id}").json()
        assert b_after["total_copies"] == 3
        assert b_after["available_copies"] == 2
        assert len(b_after["reservations"]) == 1
        assert b_after["reservations"][0]["user_name"] == "active_user"
        # Invariant check: available == total - len(reservations)
        assert b_after["available_copies"] == b_after["total_copies"] - len(b_after["reservations"])
