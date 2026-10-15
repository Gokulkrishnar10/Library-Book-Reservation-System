"""Tests for v2.1 enhanced features:
- In-App Notifications
- Cancellation authorization (patrons cannot cancel others' reservations; admins can)
- Admin cancellation notification generation
- Multi-genre query filtering (/books/?genre=Horror,Comedy)
- Patron personal active reservations endpoint (/reservations/user/{name})
"""

import pytest
from app.models import InAppNotification, User


class TestV21Enhancements:
    @pytest.fixture(autouse=True)
    def setup_data(self, client):
        # Create test books
        b1 = client.post("/books/", json={"title": "Horror Master", "author": "H. Author", "total_copies": 5, "genre": "Horror"}).json()
        b2 = client.post("/books/", json={"title": "Comedy Gold", "author": "C. Author", "total_copies": 5, "genre": "Comedy"}).json()
        b3 = client.post("/books/", json={"title": "Scary Fun", "author": "M. Author", "total_copies": 5, "genre": "Horror, Comedy"}).json()
        self.b1_id = b1["id"]
        self.b2_id = b2["id"]
        self.b3_id = b3["id"]

    def test_multi_genre_filter(self, client):
        # Query with multi-genre
        res = client.get("/books/?genre=Horror,Comedy")
        assert res.status_code == 200
        books = res.json()
        titles = [b["title"] for b in books]
        assert "Scary Fun" in titles
        assert "Horror Master" in titles
        assert "Comedy Gold" in titles
        # Multi-genre match "Scary Fun" (matches both) should be prioritized first
        assert books[0]["title"] == "Scary Fun"

    def test_user_cannot_cancel_other_patrons_reservation(self, client):
        # Patron A reserves
        res = client.post(f"/books/{self.b1_id}/reserve", json={"user_name": "Patron Alice"}).json()
        res_id = res["id"]

        # Patron B attempts to cancel Alice's reservation
        cancel_res = client.delete(f"/reservations/{res_id}?requester_name=Patron%20Bob&requester_role=user")
        assert cancel_res.status_code == 403
        assert "only cancel your own reservations" in cancel_res.json()["detail"].lower()

    def test_patron_can_cancel_own_reservation(self, client):
        res = client.post(f"/books/{self.b1_id}/reserve", json={"user_name": "Patron Alice"}).json()
        res_id = res["id"]

        # Alice cancels her own reservation
        cancel_res = client.delete(f"/reservations/{res_id}?requester_name=Patron%20Alice&requester_role=user")
        assert cancel_res.status_code == 204

    def test_admin_cancellation_creates_in_app_notification(self, client, db):
        # Alice registers
        client.post("/auth/register", json={"email": "alice@example.com", "name": "Patron Alice"})

        # Alice reserves
        res = client.post(f"/books/{self.b1_id}/reserve", json={"user_name": "Patron Alice"}).json()
        res_id = res["id"]

        # Admin cancels Alice's reservation
        del_res = client.delete(f"/reservations/{res_id}?requester_name=System%20Admin&requester_role=admin")
        assert del_res.status_code == 204

        # Check in-app notification in DB
        notif = db.query(InAppNotification).filter(InAppNotification.user_name == "Patron Alice").first()
        assert notif is not None
        assert "canceled" in notif.message.lower() or "administrator" in notif.message.lower()
        assert not notif.is_read

        # Query via notifications endpoint
        list_res = client.get("/notifications/?email=alice@example.com&name=Patron%20Alice")
        assert list_res.status_code == 200
        notifs = list_res.json()
        assert len(notifs) >= 1
        notif_id = notifs[0]["id"]

        # Mark notification as read
        read_res = client.post(f"/notifications/{notif_id}/read")
        assert read_res.status_code == 200
        assert read_res.json()["status"] == "success"

        # Verify is_read is True
        db.refresh(notif)
        assert notif.is_read is True

    def test_user_personal_reservations_endpoint(self, client):
        # Alice reserves two books
        client.post(f"/books/{self.b1_id}/reserve", json={"user_name": "Patron Alice"})
        client.post(f"/books/{self.b2_id}/reserve", json={"user_name": "Patron Alice"})

        res = client.get("/reservations/user/Patron%20Alice")
        assert res.status_code == 200
        reservations = res.json()
        assert len(reservations) == 2
        titles = [r["book_title"] for r in reservations]
        assert "Horror Master" in titles
        assert "Comedy Gold" in titles
