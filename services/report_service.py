"""Reporting and CSV export."""
from __future__ import annotations

import csv
import os
from datetime import datetime
from typing import Dict, List, Tuple

from app.config import EXPORTS_DIR
from database.connection import db
from utils.logger import get_logger

logger = get_logger(__name__)


class ReportService:
    def sales_summary(self, days: int = 30) -> Dict[str, float]:
        row = db.fetchone(
            "SELECT COUNT(*) AS orders, COALESCE(SUM(total),0) AS revenue, "
            "COALESCE(SUM(tax),0) AS tax, COALESCE(AVG(total),0) AS avg_order "
            "FROM orders WHERE created_at >= date('now','localtime',?) AND status!='Cancelled'",
            (f"-{days} days",),
        )
        return {
            "orders": row["orders"],
            "revenue": row["revenue"],
            "tax": row["tax"],
            "avg_order": row["avg_order"],
        }

    def daily_sales(self, days: int = 30) -> List[Tuple[str, int, float]]:
        rows = db.fetchall(
            "SELECT date(created_at) AS d, COUNT(*) AS orders, COALESCE(SUM(total),0) AS revenue "
            "FROM orders WHERE created_at >= date('now','localtime',?) AND status!='Cancelled' "
            "GROUP BY date(created_at) ORDER BY d DESC",
            (f"-{days} days",),
        )
        return [(r["d"], r["orders"], r["revenue"]) for r in rows]

    def category_sales(self) -> List[Tuple[str, float]]:
        rows = db.fetchall(
            "SELECT COALESCE(c.name,'Uncategorised') AS category, "
            "COALESCE(SUM(oi.line_total),0) AS revenue "
            "FROM order_items oi LEFT JOIN foods f ON f.id=oi.food_id "
            "LEFT JOIN categories c ON c.id=f.category_id "
            "GROUP BY category ORDER BY revenue DESC"
        )
        return [(r["category"], r["revenue"]) for r in rows]

    def export_daily_sales_csv(self, days: int = 30) -> str:
        os.makedirs(EXPORTS_DIR, exist_ok=True)
        path = os.path.join(EXPORTS_DIR, f"sales_{datetime.now():%Y%m%d_%H%M%S}.csv")
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["Date", "Orders", "Revenue"])
            for d, orders, revenue in self.daily_sales(days):
                writer.writerow([d, orders, f"{revenue:.2f}"])
        logger.info("Exported sales report to %s", path)
        return path


report_service = ReportService()
