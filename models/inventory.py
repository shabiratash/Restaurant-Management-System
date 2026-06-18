"""Inventory item model."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional


@dataclass
class InventoryItem:
    id: int
    name: str
    unit: str
    quantity: float
    reorder_level: float
    updated_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "InventoryItem":
        keys = row.keys()
        return cls(
            id=row["id"],
            name=row["name"],
            unit=row["unit"],
            quantity=row["quantity"],
            reorder_level=row["reorder_level"],
            updated_at=row["updated_at"] if "updated_at" in keys else None,
        )

    @property
    def is_low(self) -> bool:
        return self.quantity <= self.reorder_level
