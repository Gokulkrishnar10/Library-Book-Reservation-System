"""Email notification and credential dispatch service.

Connects to Gmail SMTP (or configured SMTP server) using credentials from .env.
Provides dual-mode operation:
- Live SMTP mode (ENABLE_LIVE_EMAIL=true): sends real emails.
- Mock / Fallback mode: logs email contents to audit log and console without failing.
"""

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


def reload_env():
    if os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("TESTING") == "true":
        return
    if ENV_PATH.exists():
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()
        except Exception:
            pass


def get_smtp_config():
    reload_env()
    is_testing = bool(os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("TESTING") == "true")
    live_val = os.environ.get("ENABLE_LIVE_EMAIL", "false").strip().lower()
    return {
        "host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "user": os.environ.get("SMTP_USER", ""),
        "password": os.environ.get("SMTP_PASSWORD", "").replace(" ", ""),
        "from_email": os.environ.get("SMTP_FROM", ""),
        "live": False if is_testing else (live_val in ("true", "1", "yes")),
    }



def send_email(to_email: str, subject: str, text_body: str, html_body: str | None = None) -> bool:
    """Send an email using SMTP. Returns True if sent successfully, False otherwise."""
    cfg = get_smtp_config()

    if not cfg["live"] or not cfg["user"] or not cfg["password"]:
        print(f"[EMAIL MOCK] To: {to_email} | Subject: {subject}\n{text_body}")
        return True

    msg = EmailMessage()
    msg["Subject"] = subject
    from_addr = cfg["from_email"] or cfg["user"]
    msg["From"] = f"Library Reservation System <{from_addr}>"
    msg["To"] = to_email
    msg.set_content(text_body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=12) as server:
            server.starttls()
            server.login(cfg["user"], cfg["password"])
            server.send_message(msg)
        print(f"[EMAIL SENT] Successfully dispatched to {to_email} (Subject: {subject})")
        return True
    except Exception as exc:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {exc}")
        return False


def send_registration_password(to_email: str, name: str, password: str) -> bool:
    subject = "Your Library System Login Credentials"
    text_body = f"""Hello {name},

Welcome to the Library Book Reservation System!

Your account has been successfully created. Here are your login credentials:
  - Login Email: {to_email}
  - 8-Character Password: {password}

You can log in right now to browse the book catalog, check book availability, and reserve copies.

Best regards,
Library Management Team
"""
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 540px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #4f46e5; margin-top: 0;">Welcome to the Library System</h2>
        <p>Hello <strong>{name}</strong>,</p>
        <p>Your library patron account has been created. Use the following credentials to log in:</p>
        <div style="background: #f8fafc; border-left: 4px solid #4f46e5; padding: 12px 16px; margin: 16px 0;">
            <p style="margin: 4px 0;"><strong>Email:</strong> {to_email}</p>
            <p style="margin: 4px 0;"><strong>Password:</strong> <code style="font-size: 18px; color: #4338ca; font-weight: bold; background: #e0e7ff; padding: 2px 6px; border-radius: 4px;">{password}</code></p>
        </div>
        <p style="color: #64748b; font-size: 13px;">Please keep this password secure. You can use it to log in and reserve books anytime.</p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;" />
        <p style="color: #94a3b8; font-size: 12px; margin: 0;">Library Book Reservation System</p>
    </div>
    """
    return send_email(to_email, subject, text_body, html_body)


def send_password_reset(to_email: str, name: str, new_password: str) -> bool:
    subject = "Library System — Password Reset Request"
    text_body = f"""Hello {name},

A password reset was requested for your library account ({to_email}).

Your new 8-character login password is:
  {new_password}

Please use this new password to log in.

If you did not request this reset, please contact the library administration immediately.

Best regards,
Library Management Team
"""
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 540px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #dc2626; margin-top: 0;">Password Reset Request</h2>
        <p>Hello <strong>{name}</strong>,</p>
        <p>Your password has been successfully reset. Here is your new login password:</p>
        <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 12px 16px; margin: 16px 0;">
            <p style="margin: 4px 0;"><strong>New Password:</strong> <code style="font-size: 18px; color: #b91c1c; font-weight: bold; background: #fee2e2; padding: 2px 6px; border-radius: 4px;">{new_password}</code></p>
        </div>
        <p style="color: #64748b; font-size: 13px;">Use this password to log into your account.</p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;" />
        <p style="color: #94a3b8; font-size: 12px; margin: 0;">Library Book Reservation System</p>
    </div>
    """
    return send_email(to_email, subject, text_body, html_body)


def send_restock_alert(to_email: str, book_title: str, book_id: int) -> bool:
    subject = f"Book Restock Alert: \"{book_title}\" is now available!"
    text_body = f"""Hello,

Good news! A copy of "{book_title}" has just become available in our library catalog.

Since you were on the waitlist for this book, you can now log in and reserve your copy before it is taken:
  Book: {book_title}
  Catalog ID: {book_id}

Best regards,
Library Book Reservation System
"""
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 540px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #059669; margin-top: 0;">Book Available for Reservation!</h2>
        <p>Good news! A copy of <strong>"{book_title}"</strong> is back in stock.</p>
        <div style="background: #ecfdf5; border-left: 4px solid #059669; padding: 12px 16px; margin: 16px 0;">
            <p style="margin: 4px 0; font-size: 16px; color: #065f46;"><strong>{book_title}</strong> is now available.</p>
        </div>
        <p>As you were on the restock notification waitlist, be sure to reserve your copy promptly before stock runs out!</p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;" />
        <p style="color: #94a3b8; font-size: 12px; margin: 0;">Library Book Reservation System</p>
    </div>
    """
    return send_email(to_email, subject, text_body, html_body)
