"""In-app notifications router.

Allows patrons to view alerts when an admin cancels their reservation,
and mark notifications as read.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import schemas, services
from app.database import get_db

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=list[schemas.NotificationOut])
def get_user_notifications(
    email: str = Query(..., description="User's email address"),
    name: Optional[str] = Query(None, description="User's full name"),
    db: Session = Depends(get_db),
):
    """Retrieve up to 30 recent in-app notifications for the given user."""
    return services.get_in_app_notifications(db, user_email=email, user_name=name)


@router.post("/{notification_id}/read", status_code=status.HTTP_200_OK)
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    """Mark an individual notification as read."""
    success = services.mark_notification_read(db, notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "success", "id": notification_id}


@router.post("/read-all", status_code=status.HTTP_200_OK)
def mark_all_as_read(
    email: str = Query(..., description="User's email address"),
    db: Session = Depends(get_db),
):
    """Mark all unread notifications for this email as read."""
    count = services.mark_all_notifications_read(db, user_email=email)
    return {"status": "success", "marked_read": count}
