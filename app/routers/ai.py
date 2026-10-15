"""AI book recommendation and natural language discovery router.

Uses Groq Cloud LLM inference (with fallback to catalog keyword matching).
Enables patrons to ask questions via voice or text and receive conversational recommendations.
"""

import json
import os
import re
import urllib.request
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import load_dotenv_file
from app.database import get_db
from app.models import Book

load_dotenv_file()

router = APIRouter(prefix="/ai", tags=["ai"])


class AiRecommendIn(BaseModel):
    query: str = Field(min_length=1, max_length=500)


class RecommendedBookBrief(BaseModel):
    id: int
    title: str
    author: str
    genre: str


class AiRecommendOut(BaseModel):
    response: str
    recommended_book_ids: list[int] = []
    recommended_books: list[RecommendedBookBrief] = []



def _call_groq_llm(query: str, catalog: list[dict], api_key: str) -> Optional[dict]:
    """Call Groq API using standard urllib with custom user-agent."""
    # Build a compact catalog context (up to 40 books across genres)
    catalog_lines = [
        f"ID: {b['id']} | Title: \"{b['title']}\" | Author: {b['author']} | Genre: {b['genre']} | Copies Available: {b['available_copies']}"
        for b in catalog[:45]
    ]
    catalog_text = "\n".join(catalog_lines)

    system_prompt = (
        "You are an expert, warm, and helpful library assistant. "
        "Recommend 1 to 3 books strictly from our active catalog below that best match the patron's query. "
        "Keep your response concise, friendly, and natural for speech (under 75 words). "
        "State the book title, author, genre, and whether it has copies available right now.\n\n"
        f"LIBRARY CATALOG:\n{catalog_text}"
    )

    body = json.dumps({
        "model": "qwen/qwen3.8-27b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        "temperature": 0.5,
        "max_tokens": 350,
    }).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "LibraryReservationSystem/2.0",
    }

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data.get("choices", [{}])[0].get("message", {})
            content = msg.get("content") or msg.get("reasoning") or ""
            if content.strip():
                return {"content": content.strip()}
            return None
    except Exception as e:
        print(f"[AI GROQ FALLBACK] Groq API call failed: {e}")
        return None



def _local_catalog_search(query: str, catalog: list[dict]) -> str:
    """Fallback keyword search if Groq API is offline."""
    q_words = set(query.lower().split())
    matches = []
    for b in catalog:
        score = 0
        text = f"{b['title']} {b['author']} {b['genre']}".lower()
        for w in q_words:
            if w in text:
                score += 1
        if score > 0:
            matches.append((score, b))

    matches.sort(key=lambda x: x[0], reverse=True)
    if not matches:
        # Default recommendation
        sample = catalog[0] if catalog else None
        if sample:
            return f"I couldn't find a direct match, but I highly recommend \"{sample['title']}\" by {sample['author']} in our {sample['genre']} section!"
        return "I couldn't find any matching books in the catalog right now. Try searching for a specific genre or title!"

    top = [m[1] for m in matches[:2]]
    recs = []
    for b in top:
        status_text = "copies are available right now" if b["available_copies"] > 0 else "currently out of stock"
        recs.append(f"\"{b['title']}\" by {b['author']} ({b['genre']}, {status_text})")

    return "Based on your request, I recommend: " + " and ".join(recs) + "."


@router.post(
    "/recommend",
    response_model=AiRecommendOut,
    summary="Get natural language book recommendations via Groq AI or smart catalog search",
)
def recommend_books(payload: AiRecommendIn, db: Session = Depends(get_db)):
    books = db.query(Book).all()

    # Prioritize books matching user query words (genres, author, title)
    q_words = set(re.findall(r"\w+", payload.query.lower()))

    def relevance(b: Book) -> int:
        score = 0
        text = f"{b.title} {b.author} {b.genre}".lower()
        for w in q_words:
            if w in text:
                score += 5
        return score

    sorted_books = sorted(books, key=relevance, reverse=True)

    catalog = [
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "genre": b.genre,
            "available_copies": b.available_copies,
            "total_copies": b.total_copies,
        }
        for b in sorted_books
    ]

    api_key = os.environ.get("GROQ_API_KEY", "")
    llm_res = None
    if api_key and not api_key.startswith("gsk_your"):
        llm_res = _call_groq_llm(payload.query, catalog, api_key)

    if llm_res and llm_res.get("content") and llm_res["content"].strip():
        response_text = llm_res["content"].strip()
    else:
        response_text = _local_catalog_search(payload.query, catalog)



    # Detect which book IDs were mentioned in the recommendation
    recommended_ids = []
    recommended_books = []
    for b in catalog:
        clean_title = b["title"].split(":")[0].split(" - ")[0].strip().lower()
        if b["title"].lower() in response_text.lower() or (len(clean_title) >= 4 and clean_title in response_text.lower()):
            if b["id"] not in recommended_ids:
                recommended_ids.append(b["id"])
                recommended_books.append(
                    RecommendedBookBrief(
                        id=b["id"],
                        title=b["title"],
                        author=b["author"],
                        genre=b["genre"],
                    )
                )

    # Fallback to top query matches if LLM did not quote full titles
    if not recommended_ids and sorted_books:
        top_matches = [
            b for b in sorted_books
            if any(w in f"{b.title} {b.author} {b.genre}".lower() for w in q_words)
        ][:3]
        for b in top_matches:
            recommended_ids.append(b.id)
            recommended_books.append(
                RecommendedBookBrief(
                    id=b.id,
                    title=b.title,
                    author=b.author,
                    genre=b.genre,
                )
            )

    return AiRecommendOut(
        response=response_text,
        recommended_book_ids=recommended_ids,
        recommended_books=recommended_books,
    )

