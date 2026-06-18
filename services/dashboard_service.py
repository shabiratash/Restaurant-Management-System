"""Aggregations powering the dashboard KPIs and charts."""
from __future__ import annotations

from typing import Dict, List, Tuple

from database.connection import db
from services.table_service import table_service


class DashboardService:
    def kpis(self) -> Dict[str, float]:
        today = db.fetchone(
            "SELECT COALESCE(SUM(total),0) AS revenue, COUNT(*) AS orders "
            "FROM orders WHERE date(created_at)=date('now','localtime') "
            "AND status != 'Cancelled'"
        )
        yesterday = db.fetchone(
            "SELECT COALESCE(SUM(total),0) AS revenue, COUNT(*) AS orders "
            "FROM orders WHERE date(created_at)=date('now','localtime','-1 day') "
            "AND status != 'Cancelled'"
        )
        table_counts = table_service.counts()
        return {
            "revenue": today["revenue"],
            "orders": today["orders"],
            "prev_revenue": yesterday["revenue"],
            "prev_orders": yesterday["orders"],
            "active_tables": table_counts.get("Occupied", 0),
            "available_tables": table_counts.get("Available", 0),
            "reserved_tables": table_counts.get("Reserved", 0),
        }

    def revenue_trend(self, days: int = 7) -> List[Tuple[str, float]]:
        rows = db.fetchall(
            "SELECT date(created_at) AS d, COALESCE(SUM(total),0) AS revenue "
            "FROM orders WHERE created_at >= date('now','localtime',?) "
            "AND status != 'Cancelled' GROUP BY date(created_at) ORDER BY d",
            (f"-{days - 1} days",),
        )
        return [(r["d"], r["revenue"]) for r in rows]

    def top_foods(self, limit: int = 5) -> List[Tuple[str, int]]:
        rows = db.fetchall(
            "SELECT food_name, SUM(quantity) AS qty FROM order_items "
            "GROUP BY food_name ORDER BY qty DESC LIMIT ?",
            (limit,),
        )
        return [(r["food_name"], r["qty"]) for r in rows]

    def inventory_usage(self, limit: int = 6) -> List[Tuple[str, float, float]]:
        rows = db.fetchall(
            "SELECT name, quantity, reorder_level FROM inventory_items "
            "ORDER BY (quantity * 1.0 / NULLIF(reorder_level,0)) ASC LIMIT ?",
            (limit,),
        )
        return [(r["name"], r["quantity"], r["reorder_level"]) for r in rows]


dashboard_service = DashboardService()
