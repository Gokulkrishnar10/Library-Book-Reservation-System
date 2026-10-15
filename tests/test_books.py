"""Tests for POST /books/ and GET /books/ and GET /books/{book_id}."""

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


# ---------------------------------------------------------------------------
# POST /books/
# ---------------------------------------------------------------------------

class TestCreateBook:
    def test_create_returns_201_and_body(self, client):
        r = create_book(client, total_copies=5)
        assert r.status_code == 201
        body = r.json()
        assert body["title"] == "Test Book"
        assert body["author"] == "Test Author"
        assert body["total_copies"] == 5
        assert body["available_copies"] == 5  # must equal total on creation
        assert "id" in body

    def test_available_equals_total_on_creation(self, client):
        r = create_book(client, total_copies=2)
        body = r.json()
        assert body["available_copies"] == body["total_copies"]

    def test_blank_title_returns_422(self, client):
        r = client.post("/books/", json={"title": "", "author": "A", "total_copies": 1})
        assert r.status_code == 422

    def test_whitespace_only_title_returns_422(self, client):
        r = client.post("/books/", json={"title": "   ", "author": "A", "total_copies": 1})
        assert r.status_code == 422

    def test_blank_author_returns_422(self, client):
        r = client.post("/books/", json={"title": "T", "author": "", "total_copies": 1})
        assert r.status_code == 422

    def test_zero_copies_returns_422(self, client):
        r = client.post("/books/", json={"title": "T", "author": "A", "total_copies": 0})
        assert r.status_code == 422

    def test_negative_copies_returns_422(self, client):
        r = client.post("/books/", json={"title": "T", "author": "A", "total_copies": -1})
        assert r.status_code == 422

    def test_non_int_copies_returns_422(self, client):
        r = client.post("/books/", json={"title": "T", "author": "A", "total_copies": "abc"})
        assert r.status_code == 422

    def test_missing_field_returns_422(self, client):
        r = client.post("/books/", json={"title": "T", "total_copies": 1})
        assert r.status_code == 422

    def test_title_over_200_chars_returns_422(self, client):
        r = client.post("/books/", json={"title": "x" * 201, "author": "A", "total_copies": 1})
        assert r.status_code == 422

    def test_title_stripped_of_whitespace(self, client):
        r = create_book(client, title="  Hello  ")
        assert r.status_code == 201
        assert r.json()["title"] == "Hello"


# ---------------------------------------------------------------------------
# GET /books/
# ---------------------------------------------------------------------------

class TestListBooks:
    def test_empty_list(self, client):
        r = client.get("/books/")
        assert r.status_code == 200
        assert r.json() == []

    def test_returns_created_books(self, client):
        create_book(client, title="B1")
        create_book(client, title="B2")
        r = client.get("/books/")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_ordered_by_id(self, client):
        create_book(client, title="Alpha")
        create_book(client, title="Beta")
        create_book(client, title="Gamma")
        titles = [b["title"] for b in client.get("/books/").json()]
        assert titles == ["Alpha", "Beta", "Gamma"]


# ---------------------------------------------------------------------------
# GET /books/{book_id}
# ---------------------------------------------------------------------------

class TestGetBook:
    def test_returns_200_with_empty_reservations(self, client):
        book_id = create_book(client).json()["id"]
        r = client.get(f"/books/{book_id}")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == book_id
        assert body["reservations"] == []

    def test_unknown_book_returns_404(self, client):
        r = client.get("/books/999")
        assert r.status_code == 404

    def test_non_integer_id_returns_422(self, client):
        r = client.get("/books/abc")
        assert r.status_code == 422
