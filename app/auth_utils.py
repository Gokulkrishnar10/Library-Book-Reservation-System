"""Cryptographic utilities for password generation and hashing."""

import hashlib
import hmac
import os
import secrets
import string


def generate_random_password(length: int = 8) -> str:
    """Generate a secure, random 8-character password.

    Ensures at least one uppercase letter, one lowercase letter, and one digit.
    """
    if length < 8:
        length = 8

    # Define character pools
    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    digits = string.digits
    special = "!@#$*"

    all_chars = upper + lower + digits + special

    # Guarantee at least 1 of each major group
    pwd = [
        secrets.choice(upper),
        secrets.choice(lower),
        secrets.choice(digits),
        secrets.choice(special),
    ]

    # Fill remaining characters
    for _ in range(length - 4):
        pwd.append(secrets.choice(all_chars))

    # Shuffle for randomness
    secrets.SystemRandom().shuffle(pwd)
    return "".join(pwd)


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a unique random 16-byte salt."""
    salt = os.urandom(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{salt.hex()}${iterations}${derived.hex()}"


def verify_password(password: str, hashed_value: str) -> bool:
    """Verify a plain password against a stored PBKDF2 hash."""
    try:
        parts = hashed_value.split("$")
        if len(parts) != 3:
            return False
        salt = bytes.fromhex(parts[0])
        iterations = int(parts[1])
        expected_hash = bytes.fromhex(parts[2])

        computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(computed, expected_hash)
    except Exception:
        return False
