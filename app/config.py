"""Central application configuration: paths and runtime constants.

All filesystem paths are resolved relative to the project root so the
application behaves identically regardless of the working directory it is
launched from.
"""
from __future__ import annotations

import os

# --- Core paths -----------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")

DB_PATH = os.path.join(DATA_DIR, "restaurant.db")

# Directories that must exist before the app starts.
REQUIRED_DIRS = (DATA_DIR, LOGS_DIR, EXPORTS_DIR, BACKUPS_DIR)


def ensure_directories() -> None:
    """Create all required runtime directories if they are missing."""
    for path in REQUIRED_DIRS:
        os.makedirs(path, exist_ok=True)


# --- Business constants ---------------------------------------------------
CURRENCY_SYMBOL = "$"
TAX_RATE = 0.08  # 8% sales tax applied at billing time.
LOW_STOCK_THRESHOLD = 10  # Default reorder threshold for inventory items.

ORDER_STATUSES = ("Pending", "Preparing", "Ready", "Served", "Cancelled")
TABLE_STATUSES = ("Available", "Reserved", "Occupied")
USER_ROLES = ("Admin", "Manager", "Cashier")
