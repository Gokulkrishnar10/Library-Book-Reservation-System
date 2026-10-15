from typing import Optional

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app import schemas, services
from app.database import get_db

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/user/{user_name}", response_model=list[schemas.UserReservationDetail])
def get_user_reservations(user_name: str, db: Session = Depends(get_db)):
    """Retrieve all active reservations for the specified user."""
    return services.get_user_reservations(db, user_name=user_name)


@router.delete(
    "/{reservation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: {"description": "Permission denied"},
        404: {"description": "Reservation not found"},
        422: {"description": "Validation error"},
    },
)
def cancel_reservation(
    reservation_id: int,
    requester_name: Optional[str] = Query(None),
    requester_role: Optional[str] = Query(None),
    x_user_name: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    name = requester_name or x_user_name
    role = requester_role or x_user_role
    services.cancel_reservation(db, reservation_id, requester_name=name, requester_role=role)

