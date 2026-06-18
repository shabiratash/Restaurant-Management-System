"""Dashboard: KPIs, live floor plan, order feed and analytics."""
from __future__ import annotations

from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGridLayout, QHBoxLayout, QLabel, QSplitter, QVBoxLayout, QWidget,
)

from app.theme import Color, Font, status_color
from models.order import Order
from services.dashboard_service import dashboard_service
from services.order_service import order_service
from services.table_service import table_service
from utils.helpers import format_currency, time_ago
from views.base_view import BaseView
from views.components.charts import BarChart, HBarChart, LineChart
from views.components.flow_layout import FlowLayout
from views.components.floor_table import FloorTable
from views.components.kpi_card import KpiCard
from views.components.widgets import Card, heading, make_button, muted


class DashboardView(BaseView):
    def __init__(self, parent=None):
        super().__init__("Dashboard", "Live overview of your restaurant", parent=parent)

        refresh = make_button("Refresh", "secondary")
        refresh.clicked.connect(self.refresh)
        self.add_action(refresh)

        self._build_kpis()
        self._build_floor_and_feed()
        self._build_analytics()
        self.refresh()

    # -- KPIs -----------------------------------------------------------
    def _build_kpis(self) -> None:
        self._kpi_host = QWidget()
        self._kpi_grid = QGridLayout(self._kpi_host)
        self._kpi_grid.setContentsMargins(0, 0, 0, 0)
        self._kpi_grid.setSpacing(16)

        self._kpi_revenue = KpiCard("Today's Revenue", "revenue", Color.PRIMARY)
        self._kpi_orders = KpiCard("Today's Orders", "orders", Color.WARNING)
        self._kpi_active = KpiCard("Active Tables", "table", Color.DANGER)
        self._kpi_available = KpiCard("Available Tables", "table", Color.SUCCESS)
        self._kpis = [self._kpi_revenue, self._kpi_orders, self._kpi_active, self._kpi_available]
        self._relayout_kpis(4)
        self.content.addWidget(self._kpi_host)

    def _relayout_kpis(self, cols: int) -> None:
        for card in self._kpis:
            self._kpi_grid.removeWidget(card)
        for i, card in enumerate(self._kpis):
            self._kpi_grid.addWidget(card, i // cols, i % cols)
        for c in range(4):
            self._kpi_grid.setColumnStretch(c, 1 if c < cols else 0)

    # -- floor + feed ---------------------------------------------------
    def _build_floor_and_feed(self) -> None:
        self._mid_split = QSplitter(Qt.Horizontal)
        self._mid_split.setChildrenCollapsible(False)
        self._mid_split.setHandleWidth(16)
        self._mid_split.setStyleSheet("QSplitter::handle { background: transparent; }")

        # Floor view
        floor_card = Card()
        head = QHBoxLayout()
        head.addWidget(heading("Restaurant Floor"))
        head.addStretch(1)
        self._legend = QLabel()
        self._legend.setText(self._legend_html())
        self._legend.setTextFormat(Qt.RichText)
        head.addWidget(self._legend)
        floor_card.body().addLayout(head)

        self._floor_host = QWidget()
        self._floor_flow = FlowLayout(self._floor_host, spacing=14)
        floor_card.body().addWidget(self._floor_host, 1)

        # Live feed
        feed_card = Card()
        feed_head = QHBoxLayout()
        feed_head.addWidget(heading("Live Order Feed"))
        feed_head.addStretch(1)
        self._feed_count = muted("")
        feed_head.addWidget(self._feed_count)
        feed_card.body().addLayout(feed_head)

        self._feed_host = QWidget()
        self._feed_layout = QVBoxLayout(self._feed_host)
        self._feed_layout.setContentsMargins(0, 0, 0, 0)
        self._feed_layout.setSpacing(10)
        feed_card.body().addWidget(self._feed_host, 1)
        feed_card.body().addStretch(1)

        self._mid_split.addWidget(floor_card)
        self._mid_split.addWidget(feed_card)
        self._mid_split.setStretchFactor(0, 3)
        self._mid_split.setStretchFactor(1, 2)
        self.content.addWidget(self._mid_split, 1)

    def _legend_html(self) -> str:
        def chip(label, color):
            return (f"<span style='color:{color};'>&#9679;</span>"
                    f"<span style='color:{Color.TEXT_SECONDARY};'> {label}&nbsp;&nbsp;</span>")
        return (chip("Available", Color.SUCCESS) + chip("Reserved", Color.WARNING)
                + chip("Occupied", Color.DANGER))

    # -- analytics ------------------------------------------------------
    def _build_analytics(self) -> None:
        self.content.addWidget(heading("Analytics"))
        self._analytics_split = QSplitter(Qt.Horizontal)
        self._analytics_split.setChildrenCollapsible(False)
        self._analytics_split.setHandleWidth(16)
        self._analytics_split.setStyleSheet("QSplitter::handle { background: transparent; }")

        rev_card = Card()
        rev_card.body().addWidget(heading("Revenue Trend (7 days)"))
        self._revenue_chart = LineChart()
        rev_card.body().addWidget(self._revenue_chart, 1)

        top_card = Card()
        top_card.body().addWidget(heading("Top Selling Foods"))
        self._top_chart = HBarChart(color=Color.SUCCESS)
        top_card.body().addWidget(self._top_chart, 1)

        self._analytics_split.addWidget(rev_card)
        self._analytics_split.addWidget(top_card)
        self._analytics_split.setStretchFactor(0, 3)
        self._analytics_split.setStretchFactor(1, 2)
        self.content.addWidget(self._analytics_split)

        self._analytics_split2 = QSplitter(Qt.Horizontal)
        self._analytics_split2.setChildrenCollapsible(False)
        self._analytics_split2.setHandleWidth(16)
        self._analytics_split2.setStyleSheet("QSplitter::handle { background: transparent; }")

        week_card = Card()
        week_card.body().addWidget(heading("Weekly Sales"))
        self._week_chart = BarChart(color=Color.PRIMARY)
        week_card.body().addWidget(self._week_chart, 1)

        inv_card = Card()
        inv_card.body().addWidget(heading("Inventory Usage"))
        self._inv_chart = HBarChart(color=Color.WARNING)
        inv_card.body().addWidget(self._inv_chart, 1)

        self._analytics_split2.addWidget(week_card)
        self._analytics_split2.addWidget(inv_card)
        self.content.addWidget(self._analytics_split2)

    # -- data refresh ---------------------------------------------------
    def refresh(self) -> None:
        k = dashboard_service.kpis()
        self._kpi_revenue.set_value(format_currency(k["revenue"]))
        self._kpi_revenue.set_trend(k["revenue"], k["prev_revenue"])
        self._kpi_orders.set_value(str(int(k["orders"])))
        self._kpi_orders.set_trend(k["orders"], k["prev_orders"])
        self._kpi_active.set_value(str(int(k["active_tables"])))
        self._kpi_active.set_subtitle(f"{int(k['reserved_tables'])} reserved")
        self._kpi_available.set_value(str(int(k["available_tables"])))
        self._kpi_available.set_subtitle("ready to seat")

        self._refresh_floor()
        self._refresh_feed()

        self._revenue_chart.set_data(dashboard_service.revenue_trend(7))
        self._top_chart.set_data([(n, q) for n, q in dashboard_service.top_foods(5)])
        self._week_chart.set_data([(d[-5:], r) for d, r in dashboard_service.revenue_trend(7)])
        self._inv_chart.set_data([(n, q) for n, q, _ in dashboard_service.inventory_usage(6)])

    def _refresh_floor(self) -> None:
        while self._floor_flow.count():
            item = self._floor_flow.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for table in table_service.list_tables():
            tile = FloorTable(table)
            tile.clicked.connect(self._cycle_table_status)
            self._floor_flow.addWidget(tile)

    def _cycle_table_status(self, table) -> None:
        order = ["Available", "Reserved", "Occupied"]
        nxt = order[(order.index(table.status) + 1) % 3] if table.status in order else "Available"
        try:
            table_service.set_status(table.id, nxt)
        except Exception:
            pass
        self._refresh_floor()
        self.refresh()

    def _refresh_feed(self) -> None:
        while self._feed_layout.count():
            item = self._feed_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        orders: List[Order] = order_service.live_feed(8)
        self._feed_count.setText(f"{len(orders)} active")
        if not orders:
            self._feed_layout.addWidget(muted("No active orders right now."))
            return
        for o in orders:
            self._feed_layout.addWidget(self._feed_row(o))

    def _feed_row(self, order: Order) -> QWidget:
        row = QWidget()
        row.setStyleSheet(
            f"background-color: {Color.BACKGROUND}; border-radius: 10px;"
        )
        lay = QHBoxLayout(row)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(10)

        col = QVBoxLayout()
        col.setSpacing(2)
        num = QLabel(f"Order #{order.id}")
        num.setStyleSheet(f"font-weight: 700; font-size: {Font.BODY}px;")
        meta = QLabel(f"{order.table_name or 'Takeaway'}  ·  {time_ago(order.created_at)}")
        meta.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: {Font.SMALL}px;")
        col.addWidget(num)
        col.addWidget(meta)
        lay.addLayout(col)
        lay.addStretch(1)

        c = status_color(order.status)
        badge = QLabel(order.status)
        badge.setStyleSheet(
            f"background-color: {c}1A; color: {c}; border-radius: 6px;"
            f" padding: 4px 12px; font-weight: 700; font-size: {Font.SMALL}px;"
        )
        lay.addWidget(badge)
        return row

    # -- responsiveness -------------------------------------------------
    def resizeEvent(self, event) -> None:
        w = self.width()
        cols = 4 if w >= 1100 else 2 if w >= 620 else 1
        current = getattr(self, "_kpi_cols", None)
        if current != cols:
            self._kpi_cols = cols
            self._relayout_kpis(cols)

        orientation = Qt.Horizontal if w >= 1000 else Qt.Vertical
        for split in (self._mid_split, self._analytics_split, self._analytics_split2):
            if split.orientation() != orientation:
                split.setOrientation(orientation)
        super().resizeEvent(event)

    def on_show(self) -> None:
        self.refresh()
