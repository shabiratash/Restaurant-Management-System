"""Authentication and current-session management."""
from __future__ import annotations

from typing import Optional

from database.connection import db
from models.user import User
from utils.exceptions import AuthenticationError, ValidationError
from utils.helpers import verify_password
from utils.logger import get_logger
from utils.validators import require_text

logger = get_logger(__name__)


class AuthService:
    def __init__(self) -> None:
        self._current: Optional[User] = None

    @property
    def current_user(self) -> Optional[User]:
        return self._current

    def login(self, username: str, password: str) -> User:
        username = require_text(username, "Username")
        if not password:
            raise ValidationError("Password is required.")

        row = db.fetchone(
            "SELECT * FROM users WHERE username = ? AND is_active = 1", (username,)
        )
        if row is None or not verify_password(password, row["password_hash"]):
            logger.warning("Failed login attempt for '%s'", username)
            raise AuthenticationError("Invalid username or password.")

        self._current = User.from_row(row)
        logger.info("User '%s' logged in (%s)", username, self._current.role)
        return self._current

    def logout(self) -> None:
        if self._current:
            logger.info("User '%s' logged out", self._current.username)
        self._current = None


# Shared session-wide instance.
auth_service = AuthService()
