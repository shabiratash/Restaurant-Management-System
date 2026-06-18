"""Restaurant table (floor) model."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class RestaurantTable:
    id: int
    name: str
    seats: int
    status: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "RestaurantTable":
        return cls(id=row["id"], name=row["name"], seats=row["seats"], status=row["status"])
