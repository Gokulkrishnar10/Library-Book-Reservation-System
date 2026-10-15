"""Tests for smart name validation rejecting numeric spam ('1234') and keyboard gibberish ('jfoienvfjov')."""

import pytest


class TestSmartNameValidation:
    @pytest.fixture(autouse=True)
    def setup_book(self, client):
        b = client.post("/books/", json={"title": "Smart Name Book", "author": "Author", "total_copies": 10}).json()
        self.book_id = b["id"]

    def test_rejects_pure_numeric_strings(self, client):
        res = client.post(f"/books/{self.book_id}/reserve", json={"user_name": "1234"})
        assert res.status_code == 422
        assert "numeric" in res.text.lower()

    def test_rejects_numeric_with_spaces_or_symbols(self, client):
        res = client.post(f"/books/{self.book_id}/reserve", json={"user_name": "  123456  "})
        assert res.status_code == 422

    def test_rejects_keyboard_consonant_spam_like_jfoienvfjov(self, client):
        # 'jfoienvfjov' contains 'nvfj' (4 consecutive consonants)
        res = client.post(f"/books/{self.book_id}/reserve", json={"user_name": "jfoienvfjov"})
        assert res.status_code == 422
        assert "unusual consonant" in res.text.lower()

    def test_rejects_keyboard_mash_asdfghjkl(self, client):
        res = client.post(f"/books/{self.book_id}/reserve", json={"user_name": "asdfghjkl"})
        assert res.status_code == 422

    def test_rejects_repetitive_characters(self, client):
        res = client.post(f"/books/{self.book_id}/reserve", json={"user_name": "aaaaaa"})
        assert res.status_code == 422
        assert "identical consecutive" in res.text.lower()

    def test_rejects_gefoinjif_keyboard_spam(self, client):
        res = client.post(f"/books/{self.book_id}/reserve", json={"user_name": "gefoinjif"})
        assert res.status_code == 422
        assert "keyboard mash" in res.text.lower() or "unusual consonant" in res.text.lower()

    def test_rejects_gegfegae_repetitive_pattern(self, client):
        res = client.post(f"/books/{self.book_id}/reserve", json={"user_name": "gegfegae"})
        assert res.status_code == 422
        assert "repetitive" in res.text.lower()

    def test_accepts_valid_human_names(self, client):
        valid_names = [
            "Alice Smith",
            "Gokul Krishna",
            "John O'Connor",
            "Mary-Jane Watson",
            "Dr. Bruce Banner",
            "user_42",
        ]
        for name in valid_names:
            res = client.post(f"/books/{self.book_id}/reserve", json={"user_name": name})
            assert res.status_code == 201, f"Expected 201 for valid name '{name}', got {res.status_code}: {res.text}"

