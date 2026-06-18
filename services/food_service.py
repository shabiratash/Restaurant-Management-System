"""Menu (foods + categories) management."""
from __future__ import annotations

from typing import List, Optional

from database.connection import db
from models.food import Category, Food
from utils.exceptions import NotFoundError
from utils.validators import require_text, validate_positive_number


class FoodService:
    # -- categories -----------------------------------------------------
    def list_categories(self) -> List[Category]:
        rows = db.fetchall("SELECT * FROM categories ORDER BY name")
        return [Category.from_row(r) for r in rows]

    def add_category(self, name: str) -> int:
        name = require_text(name, "Category name", max_len=60)
        with db.transaction() as conn:
            cur = conn.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,)
            )
        return cur.lastrowid

    # -- foods ----------------------------------------------------------
    def list_foods(self, search: str = "", category_id: Optional[int] = None) -> List[Food]:
        sql = (
            "SELECT f.*, c.name AS category_name FROM foods f "
            "LEFT JOIN categories c ON c.id = f.category_id WHERE 1=1"
        )
        params: list = []
        if search:
            sql += " AND f.name LIKE ?"
            params.append(f"%{search}%")
        if category_id:
            sql += " AND f.category_id = ?"
            params.append(category_id)
        sql += " ORDER BY f.name"
        return [Food.from_row(r) for r in db.fetchall(sql, params)]

    def create_food(self, name: str, price, category_id: Optional[int], is_available: bool = True) -> int:
        name = require_text(name, "Food name", max_len=120)
        price = validate_positive_number(price, "Price", allow_zero=True)
        with db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO foods (name, price, category_id, is_available) VALUES (?,?,?,?)",
                (name, price, category_id, int(is_available)),
            )
        return cur.lastrowid

    def update_food(self, food_id: int, name: str, price, category_id: Optional[int], is_available: bool) -> None:
        name = require_text(name, "Food name", max_len=120)
        price = validate_positive_number(price, "Price", allow_zero=True)
        with db.transaction() as conn:
            cur = conn.execute(
                "UPDATE foods SET name=?, price=?, category_id=?, is_available=? WHERE id=?",
                (name, price, category_id, int(is_available), food_id),
            )
            if cur.rowcount == 0:
                raise NotFoundError("Menu item not found.")

    def delete_food(self, food_id: int) -> None:
        with db.transaction() as conn:
            conn.execute("DELETE FROM foods WHERE id=?", (food_id,))


food_service = FoodService()
