"""Tests for out-of-stock restock waitlist: POST /books/{id}/waitlist and automatic restock triggers."""

import pytest
from app.models import WaitlistNotification


class TestWaitlist:
    def test_join_waitlist_when_out_of_stock_returns_201(self, client, db):
        # Create book with 1 copy
        b = client.post("/books/", json={"title": "Rare Book", "author": "Author", "total_copies": 1}).json()
        book_id = b["id"]

        # Reserve the only copy so available = 0
        client.post(f"/books/{book_id}/reserve", json={"user_name": "Patron One"})

        # Join waitlist
        w = client.post(f"/books/{book_id}/waitlist", json={"email": "waiter@example.com"})
        assert w.status_code == 201
        data = w.json()
        assert data["book_id"] == book_id
        assert data["user_email"] == "waiter@example.com"
        assert data["status"] == "pending"

    def test_join_waitlist_when_book_has_available_copies_returns_400(self, client):
        b = client.post("/books/", json={"title": "Plenty Book", "author": "Author", "total_copies": 3}).json()
        book_id = b["id"]

        # Copies available -> waitlist should reject with 400
        w = client.post(f"/books/{book_id}/waitlist", json={"email": "waiter@example.com"})
        assert w.status_code == 400
        assert "currently in stock" in w.json()["detail"].lower()

    def test_cancel_triggers_restock_notification_for_waitlisted_user(self, client, db):
        # Create book with 1 copy
        b = client.post("/books/", json={"title": "Stock Alert Book", "author": "Author", "total_copies": 1}).json()
        book_id = b["id"]

        # Reserve it
        res = client.post(f"/books/{book_id}/reserve", json={"user_name": "Patron Alpha"}).json()
        res_id = res["id"]

        # Waitlist user
        client.post(f"/books/{book_id}/waitlist", json={"email": "notify_me@example.com"})

        # Cancel reservation -> copy restored -> waitlist should transition to 'notified'
        client.delete(f"/reservations/{res_id}")

        # Verify waitlist record status updated in db
        w_record = (
            db.query(WaitlistNotification)
            .filter(WaitlistNotification.book_id == book_id, WaitlistNotification.user_email == "notify_me@example.com")
            .first()
        )
        assert w_record is not None
        assert w_record.status == "notified"
        assert w_record.notified_at is not None
