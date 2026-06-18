"""Customer model."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional


@dataclass
class Customer:
    id: int
    name: str
    phone: str = ""
    email: str = ""
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Customer":
        keys = row.keys()
        return cls(
            id=row["id"],
            name=row["name"],
            phone=row["phone"] or "" if "phone" in keys else "",
            email=row["email"] or "" if "email" in keys else "",
            created_at=row["created_at"] if "created_at" in keys else None,
        )
