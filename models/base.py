"""Shared model helpers."""
from __future__ import annotations

import sqlite3
from typing import Optional


def row_get(row: Optional[sqlite3.Row], key: str, default=None):
    """Safely read a column from a sqlite3.Row that may be None."""
    if row is None:
        return default
    try:
        return row[key]
    except (IndexError, KeyError):
        return default
