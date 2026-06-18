"""Customer management."""
from __future__ import annotations

from typing import List

from database.connection import db
from models.customer import Customer
from utils.exceptions import NotFoundError
from utils.validators import require_text, validate_email, validate_phone


class CustomerService:
    def list_customers(self, search: str = "") -> List[Customer]:
        sql = "SELECT * FROM customers WHERE 1=1"
        params: list = []
        if search:
            sql += " AND (name LIKE ? OR phone LIKE ? OR email LIKE ?)"
            params += [f"%{search}%"] * 3
        sql += " ORDER BY name"
        return [Customer.from_row(r) for r in db.fetchall(sql, params)]

    def create_customer(self, name: str, phone: str, email: str) -> int:
        name = require_text(name, "Customer name", max_len=120)
        phone = validate_phone(phone)
        email = validate_email(email)
        with db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO customers (name, phone, email) VALUES (?,?,?)",
                (name, phone, email),
            )
        return cur.lastrowid

    def update_customer(self, customer_id: int, name: str, phone: str, email: str) -> None:
        name = require_text(name, "Customer name", max_len=120)
        phone = validate_phone(phone)
        email = validate_email(email)
        with db.transaction() as conn:
            cur = conn.execute(
                "UPDATE customers SET name=?, phone=?, email=? WHERE id=?",
                (name, phone, email, customer_id),
            )
            if cur.rowcount == 0:
                raise NotFoundError("Customer not found.")

    def delete_customer(self, customer_id: int) -> None:
        with db.transaction() as conn:
            conn.execute("DELETE FROM customers WHERE id=?", (customer_id,))


customer_service = CustomerService()
