"""Order and order-item models."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class OrderItem:
    food_id: Optional[int]
    food_name: str
    unit_price: float
    quantity: int
    line_total: float
    id: Optional[int] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "OrderItem":
        return cls(
            id=row["id"],
            food_id=row["food_id"],
            food_name=row["food_name"],
            unit_price=row["unit_price"],
            quantity=row["quantity"],
            line_total=row["line_total"],
        )


@dataclass
class Order:
    id: int
    status: str
    subtotal: float
    tax: float
    total: float
    table_id: Optional[int] = None
    table_name: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    user_id: Optional[int] = None
    created_at: Optional[str] = None
    items: List[OrderItem] = field(default_factory=list)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Order":
        keys = row.keys()
        return cls(
            id=row["id"],
            status=row["status"],
            subtotal=row["subtotal"],
            tax=row["tax"],
            total=row["total"],
            table_id=row["table_id"] if "table_id" in keys else None,
            table_name=row["table_name"] if "table_name" in keys else None,
            customer_id=row["customer_id"] if "customer_id" in keys else None,
            customer_name=row["customer_name"] if "customer_name" in keys else None,
            user_id=row["user_id"] if "user_id" in keys else None,
            created_at=row["created_at"] if "created_at" in keys else None,
        )
