"""Idempotent seed data.

Populates the database with a default admin account, demo menu, tables,
customers, inventory and a handful of recent orders so the dashboard has
meaningful content on first launch. Safe to run repeatedly.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from app.config import TAX_RATE
from database.connection import db
from utils.helpers import hash_password
from utils.logger import get_logger

logger = get_logger(__name__)


def _seeded() -> bool:
    row = db.fetchone("SELECT COUNT(*) AS c FROM users")
    return bool(row and row["c"] > 0)


def seed() -> None:
    if _seeded():
        return
    logger.info("Seeding database with demo data")

    with db.transaction() as conn:
        conn.executemany(
            "INSERT INTO users (username, full_name, password_hash, role) VALUES (?,?,?,?)",
            [
                ("admin", "System Administrator", hash_password("admin123"), "Admin"),
                ("manager", "Floor Manager", hash_password("manager123"), "Manager"),
                ("cashier", "Front Cashier", hash_password("cashier123"), "Cashier"),
            ],
        )

        categories = ["Starters", "Mains", "Pizza", "Burgers", "Desserts", "Beverages"]
        conn.executemany("INSERT INTO categories (name) VALUES (?)", [(c,) for c in categories])
        cat_ids = {r["name"]: r["id"] for r in conn.execute("SELECT id, name FROM categories")}

        foods = [
            ("Bruschetta", "Starters", 7.50), ("Garlic Bread", "Starters", 5.00),
            ("Caesar Salad", "Starters", 8.50), ("Grilled Salmon", "Mains", 18.90),
            ("Ribeye Steak", "Mains", 24.00), ("Chicken Alfredo", "Mains", 15.50),
            ("Margherita Pizza", "Pizza", 12.00), ("Pepperoni Pizza", "Pizza", 13.50),
            ("Veggie Pizza", "Pizza", 12.50), ("Classic Burger", "Burgers", 11.00),
            ("Cheeseburger", "Burgers", 12.00), ("BBQ Bacon Burger", "Burgers", 13.50),
            ("Tiramisu", "Desserts", 6.50), ("Cheesecake", "Desserts", 6.00),
            ("Iced Coffee", "Beverages", 4.00), ("Fresh Lemonade", "Beverages", 3.50),
            ("Sparkling Water", "Beverages", 2.50),
        ]
        conn.executemany(
            "INSERT INTO foods (name, category_id, price) VALUES (?,?,?)",
            [(n, cat_ids[c], p) for n, c, p in foods],
        )

        conn.executemany(
            "INSERT INTO restaurant_tables (name, seats, status) VALUES (?,?,?)",
            [(f"Table {i}", random.choice([2, 4, 4, 6, 8]),
              random.choice(["Available", "Available", "Occupied", "Reserved"])) for i in range(1, 13)],
        )

        conn.executemany(
            "INSERT INTO customers (name, phone, email) VALUES (?,?,?)",
            [
                ("Walk-in Guest", "", ""),
                ("Olivia Bennett", "555-0142", "olivia@example.com"),
                ("Liam Carter", "555-0188", "liam@example.com"),
                ("Sophia Nguyen", "555-0119", "sophia@example.com"),
                ("Noah Patel", "555-0173", "noah@example.com"),
            ],
        )

        conn.executemany(
            "INSERT INTO inventory_items (name, unit, quantity, reorder_level) VALUES (?,?,?,?)",
            [
                ("Tomatoes", "kg", 24, 10), ("Mozzarella", "kg", 8, 10),
                ("Beef Patties", "pcs", 45, 20), ("Salmon Fillet", "kg", 6, 8),
                ("Coffee Beans", "kg", 12, 5), ("Lemons", "kg", 4, 6),
                ("Flour", "kg", 30, 15), ("Olive Oil", "L", 9, 5),
            ],
        )

    _seed_orders()
    logger.info("Seeding complete")


def _seed_orders() -> None:
    food_rows = db.fetchall("SELECT id, name, price FROM foods")
    table_rows = db.fetchall("SELECT id FROM restaurant_tables")
    cust_rows = db.fetchall("SELECT id FROM customers")
    statuses = ["Pending", "Preparing", "Ready", "Served", "Served", "Served"]

    with db.transaction() as conn:
        now = datetime.now()
        for _ in range(28):
            created = now - timedelta(days=random.randint(0, 6),
                                      hours=random.randint(0, 12),
                                      minutes=random.randint(0, 59))
            items = random.sample(food_rows, random.randint(1, 4))
            subtotal = 0.0
            line_payload = []
            for f in items:
                qty = random.randint(1, 3)
                line = round(f["price"] * qty, 2)
                subtotal += line
                line_payload.append((f["id"], f["name"], f["price"], qty, line))
            tax = round(subtotal * TAX_RATE, 2)
            total = round(subtotal + tax, 2)
            cur = conn.execute(
                "INSERT INTO orders (table_id, customer_id, user_id, status, subtotal, tax, total, created_at)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (random.choice(table_rows)["id"], random.choice(cust_rows)["id"], 1,
                 random.choice(statuses), round(subtotal, 2), tax, total,
                 created.strftime("%Y-%m-%d %H:%M:%S")),
            )
            oid = cur.lastrowid
            conn.executemany(
                "INSERT INTO order_items (order_id, food_id, food_name, unit_price, quantity, line_total)"
                " VALUES (?,?,?,?,?,?)",
                [(oid, *p) for p in line_payload],
            )
