import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import CORS_ORIGINS
from app.routers import admin, ai, auth, books, notifications, reservations


from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from app.auth_utils import hash_password
        from app.database import SessionLocal
        from app.models import User

        admin_email = os.environ.get("ADMIN_EMAIL", "admin@library.com")
        admin_pass = os.environ.get("ADMIN_DEFAULT_PASSWORD", "AdminPass123!")
        with SessionLocal() as db:
            existing = db.query(User).filter(User.email == admin_email).first()
            if not existing:
                admin_user = User(
                    email=admin_email,
                    name="System Administrator",
                    passcode_hash=hash_password(admin_pass),
                    role="admin",
                )
                db.add(admin_user)
                db.commit()
                logger.info("Default admin created: %s", admin_email)
    except Exception as e:
        logger.warning("Could not auto-seed admin: %s", e)
    yield


def create_app() -> FastAPI:
    """Application factory — used by main.py and by tests."""
    app = FastAPI(
        title="Library Reservation API",
        version="2.0.0",
        lifespan=lifespan,
        # Stable, human-readable operationIds → clean SDK method names
        generate_unique_id_function=lambda route: route.name,
        # Required so the generated SDK defaults to http://localhost:8000
        # (without this the SDK targets http://localhost which is port 80)
        servers=[{"url": "http://localhost:8000"}],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(books.router)
    app.include_router(reservations.router)
    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(ai.router)
    app.include_router(notifications.router)

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        logger.error("Database error on %s %s: %s", request.method, request.url, exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "Unexpected error on %s %s: %s", request.method, request.url, exc
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app
