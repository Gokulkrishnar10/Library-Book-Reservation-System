"""Admin endpoints: Audit logs, system telemetry metrics, and user management."""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, Book, Reservation, User, WaitlistNotification
from app.schemas import AdminMetricsOut, AuditLogOut, UserOut, WaitlistOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/audit-logs",
    response_model=list[AuditLogOut],
    summary="Get recent audit logs across logins, registrations, reservations, and restocks",
)
def get_audit_logs(limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return logs


@router.get(
    "/metrics",
    response_model=AdminMetricsOut,
    summary="Get live library system telemetry and inventory metrics",
)
def get_admin_metrics(db: Session = Depends(get_db)):
    total_books = db.query(Book).count()
    total_copies = db.query(func.sum(Book.total_copies)).scalar() or 0
    available_copies = db.query(func.sum(Book.available_copies)).scalar() or 0
    active_reservations = db.query(Reservation).count()
    total_users = db.query(User).count()
    total_waitlist_pending = (
        db.query(WaitlistNotification)
        .filter(WaitlistNotification.status == "pending")
        .count()
    )

    return AdminMetricsOut(
        total_books=total_books,
        total_copies=int(total_copies),
        available_copies=int(available_copies),
        active_reservations=active_reservations,
        total_users=total_users,
        total_waitlist_pending=total_waitlist_pending,
    )


@router.get(
    "/users",
    response_model=list[UserOut],
    summary="List all registered users and their last login timestamps",
)
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


@router.get(
    "/waitlist",
    response_model=list[WaitlistOut],
    summary="List all out-of-stock restock waitlist requests",
)
def get_waitlist(db: Session = Depends(get_db)):
    items = db.query(WaitlistNotification).order_by(WaitlistNotification.created_at.desc()).all()
    return items
