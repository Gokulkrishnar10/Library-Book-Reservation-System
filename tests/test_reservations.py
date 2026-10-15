"""Tests for POST /books/{book_id}/reserve and DELETE /reservations/{reservation_id}."""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def create_book(client, title="Test Book", author="Test Author", total_copies=3):
    return client.post("/books/", json={
        "title": title,
        "author": author,
        "total_copies": total_copies,
    })


def reserve(client, book_id, user_name="alice"):
    return client.post(f"/books/{book_id}/reserve", json={"user_name": user_name})


# ---------------------------------------------------------------------------
# POST /books/{book_id}/reserve
# ---------------------------------------------------------------------------

class TestReserveBook:
    def test_reserve_success_returns_201_and_decrements_availability(self, client):
        b = create_book(client, total_copies=2).json()
        r = reserve(client, b["id"], "alice")
        assert r.status_code == 201
        res = r.json()
        assert res["book_id"] == b["id"]
        assert res["user_name"] == "alice"
        assert "id" in res
        assert "reservation_date" in res
        assert "expires_at" in res

        # Check book available_copies decremented
        b_after = client.get(f"/books/{b['id']}").json()
        assert b_after["available_copies"] == 1
        assert len(b_after["reservations"]) == 1

    def test_all_copies_reserved_then_next_returns_409(self, client):
        b = create_book(client, total_copies=3).json()
        r1 = reserve(client, b["id"], "alice")
        r2 = reserve(client, b["id"], "bob")
        r3 = reserve(client, b["id"], "charlie")
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r3.status_code == 201

        # 4th reservation must fail with 409
        r4 = reserve(client, b["id"], "dave")
        assert r4.status_code == 409
        assert "No copies available" in r4.json()["detail"]

        b_check = client.get(f"/books/{b['id']}").json()
        assert b_check["available_copies"] == 0

    def test_duplicate_user_reservation_returns_409(self, client):
        b = create_book(client, total_copies=3).json()
        r1 = reserve(client, b["id"], "alice")
        assert r1.status_code == 201

        # Same user again
        r2 = reserve(client, b["id"], "alice")
        assert r2.status_code == 409
        assert "User already has an active reservation" in r2.json()["detail"]

    def test_duplicate_user_case_insensitive_and_trimmed_returns_409(self, client):
        b = create_book(client, total_copies=3).json()
        r1 = reserve(client, b["id"], "Alice")
        assert r1.status_code == 201

        # Case-insensitive duplicate
        r2 = reserve(client, b["id"], "  alice  ")
        assert r2.status_code == 409
        assert "User already has an active reservation" in r2.json()["detail"]

    def test_same_user_can_reserve_different_books(self, client):
        b1 = create_book(client, title="B1").json()
        b2 = create_book(client, title="B2").json()
        r1 = reserve(client, b1["id"], "alice")
        r2 = reserve(client, b2["id"], "alice")
        assert r1.status_code == 201
        assert r2.status_code == 201

    def test_reserve_unknown_book_returns_404(self, client):
        r = reserve(client, 9999, "alice")
        assert r.status_code == 404

    def test_reserve_blank_user_returns_422(self, client):
        b = create_book(client).json()
        r = client.post(f"/books/{b['id']}/reserve", json={"user_name": ""})
        assert r.status_code == 422

    def test_reserve_whitespace_only_user_returns_422(self, client):
        b = create_book(client).json()
        r = client.post(f"/books/{b['id']}/reserve", json={"user_name": "   "})
        assert r.status_code == 422

    def test_reserve_user_over_100_chars_returns_422(self, client):
        b = create_book(client).json()
        r = client.post(f"/books/{b['id']}/reserve", json={"user_name": "a" * 101})
        assert r.status_code == 422

    def test_reserve_non_int_book_id_returns_422(self, client):
        r = client.post("/books/abc/reserve", json={"user_name": "alice"})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /reservations/{reservation_id}
# ---------------------------------------------------------------------------

class TestCancelReservation:
    def test_cancel_returns_204_and_increments_available_copies(self, client):
        b = create_book(client, total_copies=2).json()
        res = reserve(client, b["id"], "alice").json()
        b_after = client.get(f"/books/{b['id']}").json()
        assert b_after["available_copies"] == 1

        del_r = client.delete(f"/reservations/{res['id']}")
        assert del_r.status_code == 204
        assert del_r.text == ""

        # Available copies restored
        b_restored = client.get(f"/books/{b['id']}").json()
        assert b_restored["available_copies"] == 2
        assert len(b_restored["reservations"]) == 0

    def test_user_can_reserve_again_after_cancellation(self, client):
        b = create_book(client, total_copies=1).json()
        res = reserve(client, b["id"], "alice").json()

        # Cancel
        client.delete(f"/reservations/{res['id']}")

        # Alice reserves again
        res2 = reserve(client, b["id"], "alice")
        assert res2.status_code == 201

    def test_cancel_unknown_reservation_returns_404(self, client):
        r = client.delete("/reservations/9999")
        assert r.status_code == 404

    def test_double_cancel_returns_404_no_double_increment(self, client):
        b = create_book(client, total_copies=2).json()
        res = reserve(client, b["id"], "alice").json()

        r1 = client.delete(f"/reservations/{res['id']}")
        assert r1.status_code == 204

        r2 = client.delete(f"/reservations/{res['id']}")
        assert r2.status_code == 404

        b_check = client.get(f"/books/{b['id']}").json()
        assert b_check["available_copies"] == 2  # not 3

    def test_cancel_non_int_id_returns_422(self, client):
        r = client.delete("/reservations/abc")
        assert r.status_code == 422
