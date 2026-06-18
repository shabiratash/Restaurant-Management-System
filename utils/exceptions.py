"""Domain-specific exception hierarchy.

Using typed exceptions lets the UI distinguish recoverable user errors
(validation, auth) from unexpected failures and react appropriately.
"""
from __future__ import annotations


class AppError(Exception):
    """Base class for all application errors."""


class ValidationError(AppError):
    """Raised when user-supplied data fails validation."""


class AuthenticationError(AppError):
    """Raised when login credentials are invalid."""


class PermissionError(AppError):
    """Raised when a user lacks rights for an action."""


class DatabaseError(AppError):
    """Raised when a database operation fails."""


class NotFoundError(AppError):
    """Raised when a requested record does not exist."""
