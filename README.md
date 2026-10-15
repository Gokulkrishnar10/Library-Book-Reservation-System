# Library Book Reservation System

A full-stack Library Book Reservation System featuring inventory capacity constraints, automated reservation expiration, cancellation inventory restoral, an interactive React frontend, and a machine-generated Python SDK.

Built with **FastAPI**, **SQLite** (with **Alembic** migrations), and **React 19** (**Vite**).

---

## 📋 Features & Trick Logic Implementation

1. **Capacity Tracking & Concurrency Safety**:
   - Each book has limited physical copies; reservations beyond availability are strictly rejected.
   - Enforces atomic conditional updates (`UPDATE books SET available_copies = available_copies - 1 WHERE id = :id AND available_copies > 0`) inside SQLite's write lock to guarantee zero overbooking under concurrent requests.
2. **Automated Lazy Expiration**:
   - Reservations expire automatically after a set duration (7 days).
   - Expired holds are purged on demand upon any catalog read or reservation action without requiring external background daemons.
3. **Cancellation & Expiry Restoral**:
   - Cancelling or expiring an active reservation immediately restores the book's available copies.
4. **Duplicate Hold Prevention**:
   - Case-insensitive uniqueness check prevents a patron from holding multiple copies of the same book simultaneously.
5. **Interactive React Client**:
   - Browse catalog with real-time availability counters.
   - Live 5-second polling updates.
   - Interactive availability breakdown charts (Recharts).
   - Reserve and cancel active reservations with live expiration countdown timers.
6. **OpenAPI Standards & Swagger UI**:
   - Complete OpenAPI 3.0 specification available at `/openapi.json`.
   - Interactive Swagger documentation accessible at `/docs`.
7. **Platform Python SDK**:
   - Generated via OpenAPI Generator CLI with package name `library_sdk`.

---

## 🛠️ Prerequisites

- **Python**: 3.12+ (tested on Python 3.12.10)
- **Node.js**: v20+ / v22+ (tested on Node v26.7.0, npm 11.19.0)
- **Java**: 21 LTS (required only if regenerating the Python SDK via OpenAPI Generator CLI)

---

## ⚡ Setup & Installation

Run the one-command setup batch script from the project root:

```cmd
setupdev.bat
```

What `setupdev.bat` does:
1. Creates a Python virtual environment (`env`).
2. Installs pinned backend dependencies from `requirements.txt`.
3. Runs database migrations (`alembic upgrade head`).
4. Idempotently loads seed data (`seed_data.sql`).
5. Installs frontend dependencies in `frontend/`.

---

## 🚀 Running the Application

Start both the backend server and frontend client with a single command:

```cmd
runapplication.bat
```

Once started, access the application at:
- **Frontend Application**: `http://localhost:5173`
- **Backend API & Swagger UI**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

## 🧪 Running Tests

### Backend Unit & Integration Tests (Pytest)
Run the 79 automated backend tests (Unit, Integration, Concurrency, and Invariant tests):

```powershell
.\env\Scripts\python.exe -m pytest -v
```

---

## 📦 Platform Python SDK

The Python client SDK was synthesized using the OpenAPI Generator CLI:

```cmd
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g python -o library_sdk --additional-properties=packageName=library_sdk
```

### SDK Usage Example

```python
import library_sdk
from library_sdk.api.books_api import BooksApi
from library_sdk import ApiClient

# Initialize client pointing to backend server
client = ApiClient(library_sdk.Configuration(host="http://localhost:8000"))
api = BooksApi(client)

# Retrieve all books
books = api.list_books()
print(f"Retrieved {len(books)} books.")
for book in books:
    print(f"- {book.title} by {book.author} (Available: {book.available_copies}/{book.total_copies})")
```

---

## 📂 Project Structure

```
library-reservation/
├── alembic/                # Alembic database migration scripts
├── alembic.ini             # Alembic configuration
├── app/                    # FastAPI backend application
│   ├── routers/            # API route controllers (books, reservations, auth, admin, etc.)
│   ├── database.py         # SQLAlchemy engine, session, & PRAGMA listeners
│   ├── models.py           # Relational database models (Book, Reservation, etc.)
│   ├── schemas.py          # Pydantic request/response validation schemas
│   └── services.py         # Core business & trick logic (atomic decrements, lazy expiry)
├── frontend/               # React 19 + Vite frontend client
│   ├── src/                # UI components, Recharts visualizations, Axios API client
│   └── tests/              # Playwright E2E browser tests
├── library_sdk/            # Python SDK generated via OpenAPI Generator CLI
├── tests/                  # Pytest backend test suite (79 tests)
├── main.py                 # Application entry point
├── requirements.txt        # Pinned Python dependencies
├── seed_data.sql           # Initial seed data SQL script
├── seed_db.py              # Database seeding runner
├── setupdev.bat            # One-command environment setup script
└── runapplication.bat       # One-command execution script
```
