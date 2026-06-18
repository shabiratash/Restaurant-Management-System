"""Restaurant floor / table management."""
from __future__ import annotations

from typing import List

from app.config import TABLE_STATUSES
from database.connection import db
from models.table import RestaurantTable
from utils.exceptions import NotFoundError, ValidationError
from utils.validators import require_text, validate_int


class TableService:
    def list_tables(self) -> List[RestaurantTable]:
        rows = db.fetchall("SELECT * FROM restaurant_tables ORDER BY id")
        return [RestaurantTable.from_row(r) for r in rows]

    def create_table(self, name: str, seats) -> int:
        name = require_text(name, "Table name", max_len=40)
        seats = validate_int(seats, "Seats", minimum=1)
        with db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO restaurant_tables (name, seats) VALUES (?,?)", (name, seats)
            )
        return cur.lastrowid

    def set_status(self, table_id: int, status: str) -> None:
        if status not in TABLE_STATUSES:
            raise ValidationError("Invalid table status.")
        with db.transaction() as conn:
            cur = conn.execute(
                "UPDATE restaurant_tables SET status=? WHERE id=?", (status, table_id)
            )
            if cur.rowcount == 0:
                raise NotFoundError("Table not found.")

    def delete_table(self, table_id: int) -> None:
        with db.transaction() as conn:
            conn.execute("DELETE FROM restaurant_tables WHERE id=?", (table_id,))

    def counts(self) -> dict:
        rows = db.fetchall(
            "SELECT status, COUNT(*) AS c FROM restaurant_tables GROUP BY status"
        )
        result = {s: 0 for s in TABLE_STATUSES}
        for r in rows:
            result[r["status"]] = r["c"]
        return result


table_service = TableService()
