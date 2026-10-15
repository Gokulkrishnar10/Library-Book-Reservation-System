"""Business logic layer — all "trick logic" lives here.

Key design decisions:
  - purge_expired() issues a DELETE *first*, which takes SQLite's write lock
    immediately, preventing race conditions on available_copies.
  - available_copies is *recomputed* from surviving rows after a purge (not
    delta-adjusted), making the operation idempotent and self-healing.
  - The reserve path uses an atomic conditional UPDATE
    (WHERE available_copies > 0) as the final gating check, so concurrent
    requests cannot double-book the last copy.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session

from app.config import RESERVATION_DAYS
from app.models import AuditLog, Book, InAppNotification, Reservation, User, WaitlistNotification
from app.email_service import send_restock_alert



# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _now_utc() -> datetime:
    """Naive UTC datetime suitable for direct comparison with SQLite columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ---------------------------------------------------------------------------
# Waitlist & Restock Notifications
# ---------------------------------------------------------------------------

def trigger_restock_notifications(db: Session, book_id: int) -> int:
    """Notify users on the waitlist when a copy becomes available."""
    book = db.get(Book, book_id)
    if not book or book.available_copies <= 0:
        return 0

    pending = (
        db.query(WaitlistNotification)
        .filter(
            WaitlistNotification.book_id == book_id,
            WaitlistNotification.status == "pending",
        )
        .all()
    )
    if not pending:
        return 0

    notified_count = 0
    now = datetime.now(timezone.utc)
    for w in pending:
        send_restock_alert(w.user_email, book.title, book.id)
        w.status = "notified"
        w.notified_at = now
        audit = AuditLog(
            event_type="RESTOCK_NOTIFY",
            user_email=w.user_email,
            details=f"Restock alert sent for '{book.title}' (Book ID {book.id})",
        )
        db.add(audit)
        notified_count += 1

    db.commit()
    return notified_count


def subscribe_waitlist(db: Session, book_id: int, email: str) -> WaitlistNotification:
    """Add a user email to the restock waitlist for an out-of-stock book."""
    book = get_book_or_404(db, book_id)
    if book.available_copies > 0:
        raise HTTPException(
            status_code=400,
            detail="Book is currently in stock. You can reserve it directly!",
        )

    existing = (
        db.query(WaitlistNotification)
        .filter(
            WaitlistNotification.book_id == book_id,
            WaitlistNotification.user_email == email,
            WaitlistNotification.status == "pending",
        )
        .first()
    )
    if existing:
        return existing

    waitlist_entry = WaitlistNotification(
        book_id=book_id,
        user_email=email,
        status="pending",
    )
    db.add(waitlist_entry)

    audit = AuditLog(
        event_type="WAITLIST_JOIN",
        user_email=email,
        details=f"Joined waitlist for '{book.title}' (Book ID {book.id})",
    )
    db.add(audit)
    db.commit()
    db.refresh(waitlist_entry)
    return waitlist_entry


# ---------------------------------------------------------------------------
# Expiry purge
# ---------------------------------------------------------------------------

def purge_expired(
    db: Session,
    now: datetime,
    book_id: Optional[int] = None,
) -> None:
    """Delete expired reservations and recompute available_copies.

    Args:
        db:      Active SQLAlchemy session.
        now:     Current UTC time (naive).  Tests may pass a custom value.
        book_id: If given, only affects that book.  Otherwise affects all books.
    """
    if book_id is not None:
        deleted = db.execute(
            text(
                "DELETE FROM reservations "
                "WHERE expires_at <= :now AND book_id = :bid"
            ),
            {"now": now, "bid": book_id},
        ).rowcount
    else:
        deleted = db.execute(
            text("DELETE FROM reservations WHERE expires_at <= :now"),
            {"now": now},
        ).rowcount

    if deleted == 0:
        return

    # Recompute available_copies from the surviving (all active) rows.
    # This is safer than a delta update: idempotent even if called twice.
    if book_id is not None:
        db.execute(
            text(
                "UPDATE books "
                "SET available_copies = total_copies - ("
                "  SELECT COUNT(*) FROM reservations r WHERE r.book_id = books.id"
                ") "
                "WHERE id = :bid"
            ),
            {"bid": book_id},
        )
        db.commit()
        trigger_restock_notifications(db, book_id)
    else:
        db.execute(
            text(
                "UPDATE books "
                "SET available_copies = total_copies - ("
                "  SELECT COUNT(*) FROM reservations r WHERE r.book_id = books.id"
                ")"
            )
        )
        db.commit()
        # Trigger restock notifications for books that gained availability
        books_with_waitlist = (
            db.query(WaitlistNotification.book_id)
            .filter(WaitlistNotification.status == "pending")
            .distinct()
            .all()
        )
        for (bid,) in books_with_waitlist:
            trigger_restock_notifications(db, bid)


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def get_book_or_404(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def list_books(db: Session, genre: Optional[str] = None) -> list[Book]:
    """Purge expired reservations globally, then return books optionally filtered by genre.

    Supports single genre (e.g. 'Horror') or multiple comma-separated genres (e.g. 'Horror,Comedy').
    When multiple genres are selected, books matching all selected genres are ranked first,
    followed by books matching any of the selected genres.
    """
    purge_expired(db, _now_utc())
    query = db.query(Book)
    if not genre or not genre.strip():
        return query.order_by(Book.id).all()

    genres = [g.strip() for g in genre.split(",") if g.strip()]
    if len(genres) == 1:
        g = genres[0]
        query = query.filter(Book.genre.ilike(f"%{g}%"))
        return query.order_by(Book.id).all()

    # Multiple genres: retrieve books matching any of the genres
    conditions = [Book.genre.ilike(f"%{g}%") for g in genres]
    books = query.filter(or_(*conditions)).all()

    # Prioritize: books matching ALL selected genres first, then partial matches
    def sort_score(book: Book) -> tuple[int, int]:
        b_genre = (book.genre or "").lower()
        match_count = sum(1 for g in genres if g.lower() in b_genre)
        return (-match_count, book.id)

    books.sort(key=sort_score)
    return books



def get_book_detail(db: Session, book_id: int) -> tuple[Book, list[Reservation]]:
    """Purge expired for this book, then return book + its active reservations."""
    now = _now_utc()
    purge_expired(db, now, book_id=book_id)
    book = get_book_or_404(db, book_id)
    reservations = (
        db.query(Reservation)
        .filter(Reservation.book_id == book_id)
        .all()
    )
    return book, reservations


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------

def create_book(
    db: Session,
    title: str,
    author: str,
    total_copies: int,
    genre: str = "General",
) -> Book:
    book = Book(
        title=title,
        author=author,
        total_copies=total_copies,
        available_copies=total_copies,
        genre=genre or "General",
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def reserve_book(
    db: Session,
    book_id: int,
    user_name: str,
    now: Optional[datetime] = None,
) -> Reservation:
    """Reserve a copy of a book for the given user."""
    if now is None:
        now = _now_utc()

    # Step 1 — 404 guard (before acquiring write lock)
    book = get_book_or_404(db, book_id)

    # Step 2 — Purge expired (acquires write lock via the DELETE)
    purge_expired(db, now, book_id=book_id)

    # Step 3 — Duplicate reservation check
    existing = (
        db.query(Reservation)
        .filter(
            Reservation.book_id == book_id,
            text("lower(trim(user_name)) = lower(trim(:uname))"),
        )
        .params(uname=user_name)
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="User already has an active reservation for this book",
        )

    # Step 4 — Atomic conditional decrement (the concurrency backstop)
    result = db.execute(
        text(
            "UPDATE books "
            "SET available_copies = available_copies - 1 "
            "WHERE id = :bid AND available_copies > 0"
        ),
        {"bid": book_id},
    )
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No copies available for this book",
        )

    # Step 5 — Persist reservation
    expires = now + timedelta(days=RESERVATION_DAYS)
    reservation = Reservation(
        book_id=book_id,
        user_name=user_name,
        expires_at=expires,
    )
    db.add(reservation)

    # Add audit log
    audit = AuditLog(
        event_type="RESERVE",
        user_email=user_name if "@" in user_name else None,
        details=f"Reservation made by '{user_name}' for book ID {book_id} ('{book.title}')",
    )
    db.add(audit)
    db.commit()
    db.refresh(reservation)
    return reservation


def cancel_reservation(
    db: Session,
    reservation_id: int,
    requester_name: Optional[str] = None,
    requester_role: Optional[str] = None,
) -> None:
    """Cancel an active reservation, restore stock, and trigger waitlist notifications.

    Only the reservation owner or an administrator can cancel a reservation.
    If an admin cancels a user's reservation, an in-app notification is sent to the user.
    """
    now = _now_utc()

    # Purge expired globally first, so expired rows cannot be "cancelled"
    purge_expired(db, now)

    reservation = db.get(Reservation, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    book_id = reservation.book_id
    user_name = reservation.user_name

    # Check permission
    is_admin = (requester_role or "").lower() == "admin"
    if requester_name and not is_admin:
        if requester_name.strip().lower() != user_name.strip().lower():
            raise HTTPException(
                status_code=403,
                detail="You can only cancel your own reservations unless you are an administrator.",
            )

    book = db.get(Book, book_id)
    book_title = book.title if book else f"Book #{book_id}"

    db.delete(reservation)
    db.flush()  # execute DELETE before the UPDATE below

    # Recompute available_copies for this book
    db.execute(
        text(
            "UPDATE books "
            "SET available_copies = total_copies - ("
            "  SELECT COUNT(*) FROM reservations r WHERE r.book_id = books.id"
            ") "
            "WHERE id = :bid"
        ),
        {"bid": book_id},
    )

    # If canceled by admin on behalf of a patron, dispatch an in-app notification!
    if is_admin and (not requester_name or requester_name.strip().lower() != user_name.strip().lower()):
        patron = db.query(User).filter(func.lower(User.name) == func.lower(user_name.strip())).first()
        target_email = patron.email if patron else (user_name if "@" in user_name else f"{user_name.lower().replace(' ', '')}@library.app")
        notif = InAppNotification(
            user_email=target_email,
            user_name=user_name,
            title="Reservation Canceled by Administrator",
            message=f"Administrator has canceled your reservation for '{book_title}'.",
            is_read=False,
        )
        db.add(notif)

    # Add audit log
    audit = AuditLog(
        event_type="CANCEL",
        user_email=requester_name or user_name,
        details=f"Reservation {reservation_id} for '{book_title}' cancelled by '{requester_name or user_name}' (role: {requester_role or 'user'})",
    )
    db.add(audit)
    db.commit()

    # Notify waitlisted users that a copy is back in stock!
    trigger_restock_notifications(db, book_id)


def get_user_reservations(db: Session, user_name: str) -> list[dict]:
    """Retrieve all active reservations for a patron with book details."""
    purge_expired(db, _now_utc())
    rows = (
        db.query(Reservation, Book)
        .join(Book, Reservation.book_id == Book.id)
        .filter(func.lower(Reservation.user_name) == func.lower(user_name.strip()))
        .order_by(Reservation.expires_at.asc())
        .all()
    )
    results = []
    for r, b in rows:
        results.append({
            "id": r.id,
            "book_id": b.id,
            "book_title": b.title,
            "book_author": b.author,
            "book_genre": b.genre,
            "user_name": r.user_name,
            "reservation_date": r.reservation_date,
            "expires_at": r.expires_at,
        })
    return results


def get_in_app_notifications(db: Session, user_email: str, user_name: Optional[str] = None) -> list[InAppNotification]:
    """Fetch recent in-app notifications for a user."""
    query = db.query(InAppNotification)
    if user_name:
        query = query.filter(
            or_(
                func.lower(InAppNotification.user_email) == func.lower(user_email.strip()),
                func.lower(InAppNotification.user_name) == func.lower(user_name.strip()),
            )
        )
    else:
        query = query.filter(func.lower(InAppNotification.user_email) == func.lower(user_email.strip()))
    return query.order_by(InAppNotification.created_at.desc()).limit(30).all()


def mark_notification_read(db: Session, notification_id: int) -> bool:
    """Mark a specific notification as read."""
    notif = db.get(InAppNotification, notification_id)
    if notif:
        notif.is_read = True
        db.commit()
        return True
    return False


def mark_all_notifications_read(db: Session, user_email: str) -> int:
    """Mark all unread notifications for a user as read."""
    count = db.query(InAppNotification).filter(
        func.lower(InAppNotification.user_email) == func.lower(user_email.strip()),
        InAppNotification.is_read == False,
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return count

