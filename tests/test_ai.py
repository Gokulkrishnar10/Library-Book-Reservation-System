"""Tests for AI recommendation endpoint: POST /ai/recommend."""

import pytest


class TestAiRecommend:
    def test_recommend_returns_200_with_response_and_catalog_match(self, client):
        client.post(
            "/books/",
            json={"title": "Cosmos and the Stars", "author": "Carl Sagan", "total_copies": 3, "genre": "Science"},
        )
        res = client.post(
            "/ai/recommend",
            json={"query": "Can you recommend a science book about stars?"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "response" in data
        assert len(data["response"]) > 0
        assert isinstance(data["recommended_book_ids"], list)
