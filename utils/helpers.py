"""Small presentation helpers used across views."""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime

from app.config import CURRENCY_SYMBOL


def format_currency(amount: float) -> str:
    return f"{CURRENCY_SYMBOL}{amount:,.2f}"


def format_datetime(value, fmt: str = "%Y-%m-%d %H:%M") -> str:
    if not value:
        return "-"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(fmt)


def time_ago(value) -> str:
    """Return a compact relative time string (e.g. '5m ago')."""
    if not value:
        return "-"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    delta = datetime.now() - value
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    return f"{seconds // 86400}d ago"


def hash_password(password: str, salt: str | None = None) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256. Returns 'salt$hash'."""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    return secrets.compare_digest(hash_password(password, salt), stored)
