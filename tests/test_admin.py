"""Tests for admin endpoints: audit logs, telemetry metrics, and user management."""

import pytest


class TestAdminEndpoints:
    def test_get_metrics(self, client):
        client.post("/books/", json={"title": "Metric Book", "author": "Author", "total_copies": 5})
        res = client.get("/admin/metrics")
        assert res.status_code == 200
        data = res.json()
        assert "total_books" in data
        assert "total_copies" in data
        assert "available_copies" in data
        assert "active_reservations" in data
        assert "total_users" in data
        assert "total_waitlist_pending" in data

    def test_get_audit_logs(self, client):
        # Trigger an action that creates an audit log (e.g. reserve)
        b = client.post("/books/", json={"title": "Audit Book", "author": "Author", "total_copies": 2}).json()
        client.post(f"/books/{b['id']}/reserve", json={"user_name": "Audit Tester"})

        res = client.get("/admin/audit-logs")
        assert res.status_code == 200
        logs = res.json()
        assert isinstance(logs, list)
        assert len(logs) > 0
        assert "event_type" in logs[0]
        assert "details" in logs[0]

    def test_get_users(self, client):
        client.post("/auth/register", json={"email": "admin_test_user@example.com", "name": "Admin Test"})
        res = client.get("/admin/users")
        assert res.status_code == 200
        users = res.json()
        assert any(u["email"] == "admin_test_user@example.com" for u in users)
