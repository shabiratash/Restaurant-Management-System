"""Order lifecycle management with transactional integrity."""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from app.config import ORDER_STATUSES, TAX_RATE
from database.connection import db
from models.order import Order, OrderItem
from utils.exceptions import NotFoundError, ValidationError

# A pending cart line: (food_id, food_name, unit_price, quantity)
CartLine = Tuple[int, str, float, int]


class OrderService:
    def list_orders(self, status: Optional[str] = None, limit: int = 100) -> List[Order]:
        sql = (
            "SELECT o.*, t.name AS table_name, c.name AS customer_name "
            "FROM orders o "
            "LEFT JOIN restaurant_tables t ON t.id = o.table_id "
            "LEFT JOIN customers c ON c.id = o.customer_id WHERE 1=1"
        )
        params: list = []
        if status:
            sql += " AND o.status = ?"
            params.append(status)
        sql += " ORDER BY o.created_at DESC LIMIT ?"
        params.append(limit)
        return [Order.from_row(r) for r in db.fetchall(sql, params)]

    def get_order(self, order_id: int) -> Order:
        row = db.fetchone(
            "SELECT o.*, t.name AS table_name, c.name AS customer_name FROM orders o "
            "LEFT JOIN restaurant_tables t ON t.id=o.table_id "
            "LEFT JOIN customers c ON c.id=o.customer_id WHERE o.id=?",
            (order_id,),
        )
        if row is None:
            raise NotFoundError("Order not found.")
        order = Order.from_row(row)
        item_rows = db.fetchall("SELECT * FROM order_items WHERE order_id=?", (order_id,))
        order.items = [OrderItem.from_row(r) for r in item_rows]
        return order

    def live_feed(self, limit: int = 12) -> List[Order]:
        rows = db.fetchall(
            "SELECT o.*, t.name AS table_name, c.name AS customer_name FROM orders o "
            "LEFT JOIN restaurant_tables t ON t.id=o.table_id "
            "LEFT JOIN customers c ON c.id=o.customer_id "
            "WHERE o.status IN ('Pending','Preparing','Ready') "
            "ORDER BY o.created_at DESC LIMIT ?",
            (limit,),
        )
        return [Order.from_row(r) for r in rows]

    def create_order(self, lines: Sequence[CartLine], table_id: Optional[int],
                     customer_id: Optional[int], user_id: Optional[int]) -> int:
        if not lines:
            raise ValidationError("An order must contain at least one item.")

        subtotal = 0.0
        payload = []
        for food_id, name, price, qty in lines:
            if qty <= 0:
                raise ValidationError(f"Quantity for {name} must be positive.")
            line_total = round(price * qty, 2)
            subtotal += line_total
            payload.append((food_id, name, price, qty, line_total))

        subtotal = round(subtotal, 2)
        tax = round(subtotal * TAX_RATE, 2)
        total = round(subtotal + tax, 2)

        with db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO orders (table_id, customer_id, user_id, status, subtotal, tax, total)"
                " VALUES (?,?,?,'Pending',?,?,?)",
                (table_id, customer_id, user_id, subtotal, tax, total),
            )
            order_id = cur.lastrowid
            conn.executemany(
                "INSERT INTO order_items (order_id, food_id, food_name, unit_price, quantity, line_total)"
                " VALUES (?,?,?,?,?,?)",
                [(order_id, *p) for p in payload],
            )
            if table_id:
                conn.execute(
                    "UPDATE restaurant_tables SET status='Occupied' WHERE id=?", (table_id,)
                )
        return order_id

    def update_status(self, order_id: int, status: str) -> None:
        if status not in ORDER_STATUSES:
            raise ValidationError("Invalid order status.")
        with db.transaction() as conn:
            cur = conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
            if cur.rowcount == 0:
                raise NotFoundError("Order not found.")
            # Free up the table when an order is closed out.
            if status in ("Served", "Cancelled"):
                row = conn.execute("SELECT table_id FROM orders WHERE id=?", (order_id,)).fetchone()
                if row and row["table_id"]:
                    conn.execute(
                        "UPDATE restaurant_tables SET status='Available' WHERE id=?",
                        (row["table_id"],),
                    )

    def delete_order(self, order_id: int) -> None:
        with db.transaction() as conn:
            conn.execute("DELETE FROM orders WHERE id=?", (order_id,))


order_service = OrderService()
