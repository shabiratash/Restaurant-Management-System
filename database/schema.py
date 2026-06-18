"""Schema definition and initialisation.

All tables use explicit foreign keys with sensible ON DELETE behaviour,
CHECK constraints for enumerated values, and NOT NULL where appropriate to
guarantee data integrity at the storage layer.
"""
from __future__ import annotations

from database.connection import db
from utils.logger import get_logger

logger = get_logger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    full_name     TEXT    NOT NULL,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'Cashier'
                  CHECK (role IN ('Admin', 'Manager', 'Cashier')),
    is_active     INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS foods (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    price       REAL    NOT NULL CHECK (price >= 0),
    is_available INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS restaurant_tables (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL UNIQUE,
    seats     INTEGER NOT NULL DEFAULT 4 CHECK (seats > 0),
    status    TEXT    NOT NULL DEFAULT 'Available'
              CHECK (status IN ('Available', 'Reserved', 'Occupied'))
);

CREATE TABLE IF NOT EXISTS customers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    phone      TEXT,
    email      TEXT,
    created_at TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS inventory_items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL UNIQUE,
    unit          TEXT    NOT NULL DEFAULT 'unit',
    quantity      REAL    NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reorder_level REAL    NOT NULL DEFAULT 10 CHECK (reorder_level >= 0),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS orders (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    table_id      INTEGER REFERENCES restaurant_tables(id) ON DELETE SET NULL,
    customer_id   INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    user_id       INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status        TEXT    NOT NULL DEFAULT 'Pending'
                  CHECK (status IN ('Pending','Preparing','Ready','Served','Cancelled')),
    subtotal      REAL    NOT NULL DEFAULT 0 CHECK (subtotal >= 0),
    tax           REAL    NOT NULL DEFAULT 0 CHECK (tax >= 0),
    total         REAL    NOT NULL DEFAULT 0 CHECK (total >= 0),
    created_at    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS order_items (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id  INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    food_id   INTEGER REFERENCES foods(id) ON DELETE SET NULL,
    food_name TEXT    NOT NULL,
    unit_price REAL   NOT NULL CHECK (unit_price >= 0),
    quantity  INTEGER NOT NULL CHECK (quantity > 0),
    line_total REAL   NOT NULL CHECK (line_total >= 0)
);

CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_status  ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_foods_category ON foods(category_id);
"""


def initialize_schema() -> None:
    """Create all tables and indexes if they do not already exist."""
    with db.transaction() as conn:
        conn.executescript(SCHEMA)
    logger.info("Database schema verified")
