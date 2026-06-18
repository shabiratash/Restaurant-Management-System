"""Menu food and category models."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    id: int
    name: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Category":
        return cls(id=row["id"], name=row["name"])


@dataclass
class Food:
    id: int
    name: str
    price: float
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    is_available: bool = True

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Food":
        keys = row.keys()
        return cls(
            id=row["id"],
            name=row["name"],
            price=row["price"],
            category_id=row["category_id"] if "category_id" in keys else None,
            category_name=row["category_name"] if "category_name" in keys else None,
            is_available=bool(row["is_available"]) if "is_available" in keys else True,
        )
