import os
from pathlib import Path

# Project root = parent of this file's parent directory (app/)
BASE_DIR = Path(__file__).resolve().parent.parent


def load_dotenv_file():
    """Load or reload .env into os.environ."""
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()
        except Exception as e:
            print(f"[CONFIG] Warning loading .env: {e}")


load_dotenv_file()



def _get_reservation_days() -> int:
    val = os.environ.get("RESERVATION_DAYS", "7")
    try:
        days = int(val)
        if days < 1:
            raise ValueError
        return days
    except ValueError:
        raise RuntimeError(
            f"RESERVATION_DAYS must be an integer >= 1, got: {val!r}"
        )


RESERVATION_DAYS: int = _get_reservation_days()

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'library.db'}",
)

CORS_ORIGINS: list[str] = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,"
    "http://localhost:8000,http://127.0.0.1:8000",
).split(",")
