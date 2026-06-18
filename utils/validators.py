"""Reusable input validation helpers.

Each validator raises :class:`ValidationError` with a human-readable message
on failure and returns the cleaned value on success.
"""
from __future__ import annotations

import re

from utils.exceptions import ValidationError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^[0-9+\-\s()]{6,20}$")


def require_text(value: str, field: str, *, min_len: int = 1, max_len: int = 255) -> str:
    value = (value or "").strip()
    if len(value) < min_len:
        raise ValidationError(f"{field} is required.")
    if len(value) > max_len:
        raise ValidationError(f"{field} must be at most {max_len} characters.")
    return value


def validate_email(value: str, *, required: bool = False) -> str:
    value = (value or "").strip()
    if not value:
        if required:
            raise ValidationError("Email is required.")
        return ""
    if not _EMAIL_RE.match(value):
        raise ValidationError("Please enter a valid email address.")
    return value


def validate_phone(value: str, *, required: bool = False) -> str:
    value = (value or "").strip()
    if not value:
        if required:
            raise ValidationError("Phone number is required.")
        return ""
    if not _PHONE_RE.match(value):
        raise ValidationError("Please enter a valid phone number.")
    return value


def validate_positive_number(value, field: str, *, allow_zero: bool = False) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a number.")
    if number < 0 or (number == 0 and not allow_zero):
        raise ValidationError(f"{field} must be greater than {'or equal to ' if allow_zero else ''}zero.")
    return number


def validate_int(value, field: str, *, minimum: int = 0) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a whole number.")
    if number < minimum:
        raise ValidationError(f"{field} must be at least {minimum}.")
    return number
