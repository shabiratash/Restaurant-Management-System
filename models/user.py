"""User account model."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    username: str
    full_name: str
    role: str
    is_active: bool = True
    password_hash: str = ""
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "User":
        return cls(
            id=row["id"],
            username=row["username"],
            full_name=row["full_name"],
            role=row["role"],
            is_active=bool(row["is_active"]),
            password_hash=row["password_hash"] if "password_hash" in row.keys() else "",
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )

    @property
    def is_admin(self) -> bool:
        return self.role == "Admin"
