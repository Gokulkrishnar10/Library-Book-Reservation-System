from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas, services
from app.database import get_db

router = APIRouter(prefix="/books", tags=["books"])


@router.post(
    "/",
    response_model=schemas.BookOut,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"description": "Validation error"}},
)
def create_book(book_in: schemas.BookCreate, db: Session = Depends(get_db)):
    return services.create_book(
        db,
        title=book_in.title,
        author=book_in.author,
        total_copies=book_in.total_copies,
        genre=book_in.genre,
    )


@router.get("/", response_model=list[schemas.BookOut])
def list_books(genre: Optional[str] = None, db: Session = Depends(get_db)):
    return services.list_books(db, genre=genre)


@router.get(
    "/{book_id}",
    response_model=schemas.BookDetail,
    responses={
        404: {"description": "Book not found"},
        422: {"description": "Validation error"},
    },
)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book, reservations = services.get_book_detail(db, book_id)
    return schemas.BookDetail(
        id=book.id,
        title=book.title,
        author=book.author,
        total_copies=book.total_copies,
        available_copies=book.available_copies,
        genre=book.genre,
        reservations=reservations,
    )


@router.post(
    "/{book_id}/reserve",
    response_model=schemas.ReservationOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Book not found"},
        409: {"description": "No copies available or duplicate reservation"},
        422: {"description": "Validation error"},
    },
)
def reserve_book(
    book_id: int,
    body: schemas.ReserveIn,
    db: Session = Depends(get_db),
):
    return services.reserve_book(db, book_id=book_id, user_name=body.user_name)


@router.post(
    "/{book_id}/waitlist",
    response_model=schemas.WaitlistOut,
    status_code=status.HTTP_201_CREATED,
    summary="Join waitlist for an out-of-stock book to receive email alert when restocked",
    responses={
        400: {"description": "Book is already in stock"},
        404: {"description": "Book not found"},
        422: {"description": "Validation error"},
    },
)
def join_waitlist(
    book_id: int,
    body: schemas.WaitlistIn,
    db: Session = Depends(get_db),
):
    return services.subscribe_waitlist(db, book_id=book_id, email=body.email)
