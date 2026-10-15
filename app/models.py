from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Text,
    TIMESTAMP,
    CheckConstraint,
    ForeignKeyConstraint,
    text,
)

from app.database import Base


class Book(Base):
    """Maps to the `books` table (exact schema from the challenge document)."""

    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint("total_copies > 0", name="ck_books_total_positive"),
        CheckConstraint("available_copies >= 0", name="ck_books_avail_nonneg"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    author = Column(Text, nullable=False)
    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, nullable=False)
    genre = Column(Text, nullable=False, server_default="General")


class Reservation(Base):
    """Maps to the `reservations` table (exact schema from the challenge document)."""

    __tablename__ = "reservations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            ondelete="CASCADE",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, nullable=False)
    user_name = Column(Text, nullable=False)
    reservation_date = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    expires_at = Column(TIMESTAMP, nullable=False)


class User(Base):
    """Maps to the `users` table for patron and admin authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(Text, nullable=False, unique=True, index=True)
    name = Column(Text, nullable=False)
    passcode_hash = Column(Text, nullable=False)
    role = Column(Text, nullable=False, server_default="user")
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    last_login_at = Column(TIMESTAMP, nullable=True)


class WaitlistNotification(Base):
    """Maps to `waitlist_notifications` for out-of-stock restock alerts."""

    __tablename__ = "waitlist_notifications"
    __table_args__ = (
        ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            ondelete="CASCADE",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, nullable=False)
    user_email = Column(Text, nullable=False)
    status = Column(Text, nullable=False, server_default="pending")
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    notified_at = Column(TIMESTAMP, nullable=True)


class AuditLog(Base):
    """Maps to `audit_logs` tracking user events, logins, and restock alerts."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(Text, nullable=False, index=True)
    user_email = Column(Text, nullable=True)
    details = Column(Text, nullable=False)
    timestamp = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
    )


class InAppNotification(Base):
    """Maps to `in_app_notifications` for patron alerts when admin cancels reservations or account notices."""

    __tablename__ = "in_app_notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(Text, nullable=False, index=True)
    user_name = Column(Text, nullable=True)
    title = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, server_default=text("0"), index=True)
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

