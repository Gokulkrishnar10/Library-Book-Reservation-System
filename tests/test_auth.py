"""Tests for authentication endpoints: /auth/register, /auth/login, /auth/forgot-password."""

import pytest
from app.models import AuditLog, User


class TestAuthRegister:
    def test_register_success_returns_201_and_preview(self, client, db):
        res = client.post(
            "/auth/register",
            json={"email": "newpatron@example.com", "name": "Jane Doe"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == "newpatron@example.com"
        assert "password" in data["message"].lower() or "created" in data["message"].lower()
        assert len(data["dev_password_preview"]) == 8

        # Check database persistence
        user = db.query(User).filter(User.email == "newpatron@example.com").first()
        assert user is not None
        assert user.name == "Jane Doe"
        assert user.role == "user"

        # Check audit log
        audit = db.query(AuditLog).filter(AuditLog.event_type == "REGISTER").first()
        assert audit is not None
        assert "Jane Doe" in audit.details

    def test_register_duplicate_email_returns_409(self, client):
        client.post(
            "/auth/register",
            json={"email": "duplicate@example.com", "name": "User One"},
        )
        res = client.post(
            "/auth/register",
            json={"email": "duplicate@example.com", "name": "User Two"},
        )
        assert res.status_code == 409
        assert "already exists" in res.json()["detail"]


class TestAuthLogin:
    def test_login_success_and_updates_last_login(self, client, db):
        # Register first
        reg = client.post(
            "/auth/register",
            json={"email": "loginuser@example.com", "name": "Login User"},
        ).json()
        password = reg["dev_password_preview"]

        # Attempt login
        login_res = client.post(
            "/auth/login",
            json={"email": "loginuser@example.com", "password": password},
        )
        assert login_res.status_code == 200
        data = login_res.json()
        assert "token" in data
        assert data["user"]["email"] == "loginuser@example.com"
        assert data["user"]["last_login_at"] is not None

    def test_login_wrong_password_returns_401(self, client):
        client.post(
            "/auth/register",
            json={"email": "userpass@example.com", "name": "User Pass"},
        )
        res = client.post(
            "/auth/login",
            json={"email": "userpass@example.com", "password": "WrongPassword123!"},
        )
        assert res.status_code == 401
        assert "Invalid email or password" in res.json()["detail"]

    def test_login_nonexistent_email_returns_401(self, client):
        res = client.post(
            "/auth/login",
            json={"email": "ghost@example.com", "password": "randompassword"},
        )
        assert res.status_code == 401


class TestForgotPassword:
    def test_forgot_password_generates_new_passcode(self, client):
        # Register
        reg = client.post(
            "/auth/register",
            json={"email": "resetme@example.com", "name": "Reset User"},
        ).json()
        old_pass = reg["dev_password_preview"]

        # Request reset
        reset_res = client.post(
            "/auth/forgot-password",
            json={"email": "resetme@example.com"},
        )
        assert reset_res.status_code == 200
        new_pass = reset_res.json()["dev_password_preview"]
        assert len(new_pass) == 8
        assert new_pass != old_pass

        # Login with old pass must fail
        fail = client.post(
            "/auth/login",
            json={"email": "resetme@example.com", "password": old_pass},
        )
        assert fail.status_code == 401

        # Login with new pass must succeed
        ok = client.post(
            "/auth/login",
            json={"email": "resetme@example.com", "password": new_pass},
        )
        assert ok.status_code == 200

    def test_forgot_password_unknown_email_returns_404(self, client):
        res = client.post(
            "/auth/forgot-password",
            json={"email": "unknown@example.com"},
        )
        assert res.status_code == 404
