"""Reports: sales summary, category breakdown, daily table and CSV export."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView, QGridLayout, QHeaderView, QMessageBox, QTableWidget,
    QTableWidgetItem, QWidget,
)

from app.theme import Color
from services.report_service import report_service
from utils.helpers import format_currency
from utils.logger import get_logger
from views.base_view import BaseView
from views.components.charts import HBarChart
from views.components.kpi_card import KpiCard
from views.components.widgets import Card, heading, make_button

logger = get_logger(__name__)


class ReportsView(BaseView):
    def __init__(self, parent=None):
        super().__init__("Reports", "Sales performance over the last 30 days", parent=parent)
        export = make_button("Export CSV", "secondary")
        export.clicked.connect(self._export)
        self.add_action(export)

        # summary KPIs
        host = QWidget()
        grid = QGridLayout(host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(16)
        self._kpi_revenue = KpiCard("Total Revenue", "revenue", Color.PRIMARY)
        self._kpi_orders = KpiCard("Total Orders", "orders", Color.WARNING)
        self._kpi_avg = KpiCard("Avg Order Value", "revenue", Color.SUCCESS)
        self._kpi_tax = KpiCard("Tax Collected", "reports", Color.DANGER)
        self._summary_cards = [self._kpi_revenue, self._kpi_orders, self._kpi_avg, self._kpi_tax]
        self._summary_grid = grid
        self._summary_host = host
        self._relayout_summary(4)
        self.content.addWidget(host)

        # category chart
        cat_card = Card()
        cat_card.body().addWidget(heading("Revenue by Category"))
        self._cat_chart = HBarChart(color=Color.PRIMARY)
        self._cat_chart.setMinimumHeight(220)
        cat_card.body().addWidget(self._cat_chart)
        self.content.addWidget(cat_card)

        # daily table
        table_card = Card()
        table_card.body().addWidget(heading("Daily Sales"))
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Date", "Orders", "Revenue"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.setMinimumHeight(260)
        table_card.body().addWidget(self._table)
        self.content.addWidget(table_card)
        self.refresh()

    def _relayout_summary(self, cols: int) -> None:
        for c in self._summary_cards:
            self._summary_grid.removeWidget(c)
        for i, c in enumerate(self._summary_cards):
            self._summary_grid.addWidget(c, i // cols, i % cols)
        for col in range(4):
            self._summary_grid.setColumnStretch(col, 1 if col < cols else 0)

    def refresh(self) -> None:
        try:
            summary = report_service.sales_summary(30)
            self._kpi_revenue.set_value(format_currency(summary["revenue"]))
            self._kpi_revenue.set_subtitle("last 30 days")
            self._kpi_orders.set_value(str(int(summary["orders"])))
            self._kpi_orders.set_subtitle("last 30 days")
            self._kpi_avg.set_value(format_currency(summary["avg_order"]))
            self._kpi_avg.set_subtitle("per order")
            self._kpi_tax.set_value(format_currency(summary["tax"]))
            self._kpi_tax.set_subtitle("collected")

            self._cat_chart.set_data([(n, r) for n, r in report_service.category_sales()])

            rows = report_service.daily_sales(30)
            self._table.setRowCount(0)
            for d, orders, revenue in rows:
                r = self._table.rowCount()
                self._table.insertRow(r)
                self._table.setItem(r, 0, QTableWidgetItem(d))
                oi = QTableWidgetItem(str(orders))
                oi.setTextAlignment(Qt.AlignCenter)
                self._table.setItem(r, 1, oi)
                ri = QTableWidgetItem(format_currency(revenue))
                ri.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self._table.setItem(r, 2, ri)
        except Exception:
            logger.exception("Failed to build reports")

    def _export(self) -> None:
        try:
            path = report_service.export_daily_sales_csv(30)
            QMessageBox.information(self, "Export complete", f"Report saved to:\n{path}")
        except Exception:
            logger.exception("Export failed")
            QMessageBox.critical(self, "Export failed", "Could not export the report.")

    def resizeEvent(self, event) -> None:
        cols = 4 if self.width() >= 1100 else 2 if self.width() >= 620 else 1
        if getattr(self, "_cols", None) != cols:
            self._cols = cols
            self._relayout_summary(cols)
        super().resizeEvent(event)

    def on_show(self) -> None:
        self.refresh()
