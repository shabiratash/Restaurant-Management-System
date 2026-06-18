"""SQLite connection management.

A lightweight wrapper around :mod:`sqlite3` that:
  * enforces foreign keys and WAL journaling for integrity + concurrency,
  * exposes a context-managed transaction helper,
  * returns ``sqlite3.Row`` objects so callers can use column names,
  * centralises error translation into :class:`DatabaseError`.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any, Iterable, Iterator, Optional, Sequence

from app import config
from utils.exceptions import DatabaseError
from utils.logger import get_logger

logger = get_logger(__name__)


class Database:
    """Owns a single SQLite connection for the application lifetime."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        config.ensure_directories()
        self._path = db_path or config.DB_PATH
        self._conn: Optional[sqlite3.Connection] = None

    # -- connection lifecycle ------------------------------------------
    @property
    def connection(self) -> sqlite3.Connection:
        if self._conn is None:
            try:
                self._conn = sqlite3.connect(
                    self._path, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False
                )
                self._conn.row_factory = sqlite3.Row
                self._conn.execute("PRAGMA foreign_keys = ON;")
                self._conn.execute("PRAGMA journal_mode = WAL;")
                logger.info("Opened database connection at %s", self._path)
            except sqlite3.Error as exc:  # pragma: no cover - hardware level
                logger.exception("Failed to open database")
                raise DatabaseError(f"Could not open database: {exc}") from exc
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            logger.info("Closed database connection")

    # -- query helpers --------------------------------------------------
    def execute(self, sql: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        try:
            return self.connection.execute(sql, params)
        except sqlite3.Error as exc:
            logger.exception("Query failed: %s", sql)
            raise DatabaseError(str(exc)) from exc

    def fetchone(self, sql: str, params: Sequence[Any] = ()) -> Optional[sqlite3.Row]:
        return self.execute(sql, params).fetchone()

    def fetchall(self, sql: str, params: Sequence[Any] = ()) -> list[sqlite3.Row]:
        return self.execute(sql, params).fetchall()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Context manager that commits on success and rolls back on error."""
        conn = self.connection
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as exc:
            conn.rollback()
            logger.exception("Transaction rolled back")
            raise DatabaseError(str(exc)) from exc
        except Exception:
            conn.rollback()
            raise

    def executemany(self, sql: str, seq: Iterable[Sequence[Any]]) -> None:
        try:
            with self.transaction() as conn:
                conn.executemany(sql, seq)
        except sqlite3.Error as exc:
            raise DatabaseError(str(exc)) from exc


# Shared singleton used across services.
db = Database()
