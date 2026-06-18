"""Orders management: filter, create, advance status, view and delete."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView, QComboBox, QHBoxLayout, QHeaderView, QMessageBox,
    QTableWidget, QTableWidgetItem, QWidget,
)

from app.config import ORDER_STATUSES
from app.theme import Color, Font, status_color
from services.auth_service import auth_service
from services.order_service import order_service
from utils.helpers import format_currency, time_ago
from utils.logger import get_logger
from views.base_view import BaseView
from views.components.widgets import Card, make_button
from views.new_order_dialog import NewOrderDialog

logger = get_logger(__name__)


class OrdersView(BaseView):
    def __init__(self, parent=None):
        super().__init__("Orders", "Track and manage all orders", scroll=False, parent=parent)
        new_btn = make_button("+ New Order")
        new_btn.clicked.connect(self._new_order)
        self.add_action(new_btn)

        card = Card(padding=18)
        toolbar = QHBoxLayout()
        self._filter = QComboBox()
        self._filter.addItem("All statuses", None)
        for s in ORDER_STATUSES:
            self._filter.addItem(s, s)
        self._filter.setMinimumHeight(40)
        self._filter.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self._filter)
        toolbar.addStretch(1)
        card.body().addLayout(toolbar)

        self._table = QTableWidget(0, 7)
        self._table.setHorizontalHeaderLabels(
            ["Order", "Table", "Customer", "Total", "Status", "Time", "Actions"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        for col in (0, 1, 3, 4, 5):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self._table.setColumnWidth(6, 260)
        self._table.verticalHeader().setDefaultSectionSize(54)
        card.body().addWidget(self._table, 1)
        self.content.addWidget(card, 1)
        self.refresh()

    def refresh(self) -> None:
        try:
            orders = order_service.list_orders(self._filter.currentData())
        except Exception:
            logger.exception("Failed to load orders")
            orders = []
        self._table.setRowCount(0)
        for o in orders:
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setItem(r, 0, QTableWidgetItem(f"#{o.id}"))
            self._table.setItem(r, 1, QTableWidgetItem(o.table_name or "Takeaway"))
            self._table.setItem(r, 2, QTableWidgetItem(o.customer_name or "Walk-in"))
            total = QTableWidgetItem(format_currency(o.total))
            total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._table.setItem(r, 3, total)
            self._table.setCellWidget(r, 4, self._status_badge(o.status))
            self._table.setItem(r, 5, QTableWidgetItem(time_ago(o.created_at)))
            self._table.setCellWidget(r, 6, self._actions(o))

    def _status_badge(self, status: str) -> QWidget:
        host = QWidget()
        lay = QHBoxLayout(host)
        lay.setContentsMargins(6, 4, 6, 4)
        from PyQt5.QtWidgets import QLabel
        c = status_color(status)
        badge = QLabel(status)
        badge.setStyleSheet(
            f"background-color: {c}1A; color: {c}; border-radius: 6px;"
            f" padding: 4px 12px; font-weight: 700; font-size: {Font.SMALL}px;"
        )
        lay.addWidget(badge)
        lay.addStretch(1)
        return host

    def _actions(self, order) -> QWidget:
        host = QWidget()
        lay = QHBoxLayout(host)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(6)
        combo = QComboBox()
        for s in ORDER_STATUSES:
            combo.addItem(s, s)
        idx = combo.findData(order.status)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        combo.setMinimumHeight(32)
        combo.currentIndexChanged.connect(
            lambda _=0, o=order, c=combo: self._change_status(o, c.currentData()))
        delete = make_button("Delete", "danger")
        delete.setMinimumHeight(32)
        delete.clicked.connect(lambda: self._delete(order))
        lay.addWidget(combo, 1)
        lay.addWidget(delete)
        return host

    def _change_status(self, order, status: str) -> None:
        if status == order.status:
            return
        try:
            order_service.update_status(order.id, status)
        except Exception:
            logger.exception("Failed to update order status")
            QMessageBox.critical(self, "Error", "Could not update order status.")
        self.refresh()

    def _delete(self, order) -> None:
        if QMessageBox.question(self, "Delete order",
                                f"Delete order #{order.id}?") == QMessageBox.Yes:
            order_service.delete_order(order.id)
            self.refresh()

    def _new_order(self) -> None:
        user = auth_service.current_user
        dlg = NewOrderDialog(user.id if user else None, self)
        if dlg.exec_():
            self.refresh()

    def on_show(self) -> None:
        self.refresh()
