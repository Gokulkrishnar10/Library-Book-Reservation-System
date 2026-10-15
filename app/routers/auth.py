"""Authentication endpoints: Register, Login, Forgot Password."""

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, User
from app.schemas import (
    ForgotPasswordIn,
    ForgotPasswordResponse,
    LoginResponse,
    RegisterResponse,
    UserLoginIn,
    UserOut,
    UserRegisterIn,
)
from app.auth_utils import generate_random_password, hash_password, verify_password
from app.email_service import get_smtp_config, send_password_reset, send_registration_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user and email an 8-character password",
)
def register(payload: UserRegisterIn, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Generate 8-character random password
    raw_password = generate_random_password(8)
    passcode_hash = hash_password(raw_password)

    new_user = User(
        email=payload.email,
        name=payload.name,
        passcode_hash=passcode_hash,
        role="user",
    )
    db.add(new_user)

    # Audit log
    audit = AuditLog(
        event_type="REGISTER",
        user_email=payload.email,
        details=f"Patron registered: {payload.name} ({payload.email})",
    )
    db.add(audit)
    db.commit()

    # Dispatch email via Gmail SMTP
    send_registration_password(payload.email, payload.name, raw_password)

    return RegisterResponse(
        message=f"Account created successfully! Your 8-character password has been sent to {payload.email}.",
        email=payload.email,
        dev_password_preview=raw_password,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Log in with Gmail and 8-character password",
)
def login(payload: UserLoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.passcode_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Update login timestamp
    user.last_login_at = datetime.now(timezone.utc)

    # Audit log
    audit = AuditLog(
        event_type="LOGIN",
        user_email=user.email,
        details=f"User login successful: {user.name} ({user.role})",
    )
    db.add(audit)
    db.commit()
    db.refresh(user)

    # Session token
    token = secrets.token_urlsafe(32)

    return LoginResponse(
        token=token,
        user=UserOut.model_validate(user),
        message="Login successful",
    )


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Reset password and email a new 8-character password",
)
def forgot_password(payload: ForgotPasswordIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address.",
        )

    # Generate new random 8-character password
    new_password = generate_random_password(8)
    user.passcode_hash = hash_password(new_password)

    # Audit log
    audit = AuditLog(
        event_type="PASSWORD_RESET",
        user_email=user.email,
        details=f"Password reset issued for {user.name} ({user.email})",
    )
    db.add(audit)
    db.commit()

    # Dispatch reset email via Gmail SMTP
    send_password_reset(user.email, user.name, new_password)

    return ForgotPasswordResponse(
        message=f"A new 8-character password has been sent to {user.email}.",
        email=user.email,
        dev_password_preview=new_password,
    )

