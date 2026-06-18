"""Inventory management."""
from __future__ import annotations

from typing import List

from database.connection import db
from models.inventory import InventoryItem
from utils.exceptions import NotFoundError
from utils.validators import require_text, validate_positive_number


class InventoryService:
    def list_items(self, search: str = "") -> List[InventoryItem]:
        sql = "SELECT * FROM inventory_items WHERE 1=1"
        params: list = []
        if search:
            sql += " AND name LIKE ?"
            params.append(f"%{search}%")
        sql += " ORDER BY name"
        return [InventoryItem.from_row(r) for r in db.fetchall(sql, params)]

    def low_stock(self) -> List[InventoryItem]:
        rows = db.fetchall(
            "SELECT * FROM inventory_items WHERE quantity <= reorder_level ORDER BY quantity"
        )
        return [InventoryItem.from_row(r) for r in rows]

    def create_item(self, name: str, unit: str, quantity, reorder_level) -> int:
        name = require_text(name, "Item name", max_len=80)
        unit = require_text(unit, "Unit", max_len=20)
        quantity = validate_positive_number(quantity, "Quantity", allow_zero=True)
        reorder_level = validate_positive_number(reorder_level, "Reorder level", allow_zero=True)
        with db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO inventory_items (name, unit, quantity, reorder_level) VALUES (?,?,?,?)",
                (name, unit, quantity, reorder_level),
            )
        return cur.lastrowid

    def update_item(self, item_id: int, name: str, unit: str, quantity, reorder_level) -> None:
        name = require_text(name, "Item name", max_len=80)
        unit = require_text(unit, "Unit", max_len=20)
        quantity = validate_positive_number(quantity, "Quantity", allow_zero=True)
        reorder_level = validate_positive_number(reorder_level, "Reorder level", allow_zero=True)
        with db.transaction() as conn:
            cur = conn.execute(
                "UPDATE inventory_items SET name=?, unit=?, quantity=?, reorder_level=?,"
                " updated_at=datetime('now','localtime') WHERE id=?",
                (name, unit, quantity, reorder_level, item_id),
            )
            if cur.rowcount == 0:
                raise NotFoundError("Inventory item not found.")

    def delete_item(self, item_id: int) -> None:
        with db.transaction() as conn:
            conn.execute("DELETE FROM inventory_items WHERE id=?", (item_id,))


inventory_service = InventoryService()
