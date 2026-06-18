"""Inventory management with low-stock highlighting."""
from __future__ import annotations

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QAbstractItemView, QHBoxLayout, QHeaderView, QLineEdit, QMessageBox,
    QTableWidget, QTableWidgetItem, QWidget,
)

from app.theme import Color
from services.inventory_service import inventory_service
from utils.logger import get_logger
from views.base_view import BaseView
from views.components.form_dialog import FormDialog
from views.components.widgets import Card, make_button

logger = get_logger(__name__)


class InventoryView(BaseView):
    def __init__(self, parent=None):
        super().__init__("Inventory", "Track stock levels and reorder points",
                         scroll=False, parent=parent)
        add_btn = make_button("+ Add Item")
        add_btn.clicked.connect(self._add)
        self.add_action(add_btn)

        card = Card(padding=18)
        toolbar = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search inventory…")
        self._search.setMinimumHeight(40)
        self._search.textChanged.connect(self.refresh)
        toolbar.addWidget(self._search, 1)
        card.body().addLayout(toolbar)

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["Item", "Quantity", "Reorder Level", "Status", "Actions"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in (1, 2, 3, 4):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self._table.setColumnWidth(4, 170)
        self._table.verticalHeader().setDefaultSectionSize(52)
        card.body().addWidget(self._table, 1)
        self.content.addWidget(card, 1)
        self.refresh()

    def refresh(self) -> None:
        try:
            items = inventory_service.list_items(self._search.text().strip())
        except Exception:
            logger.exception("Failed to load inventory")
            items = []
        low = sum(1 for i in items if i.is_low)
        self.set_subtitle(f"Track stock levels and reorder points  ·  {low} item(s) low")
        self._table.setRowCount(0)
        for item in items:
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setItem(r, 0, QTableWidgetItem(item.name))
            self._table.setItem(r, 1, QTableWidgetItem(f"{item.quantity:g} {item.unit}"))
            self._table.setItem(r, 2, QTableWidgetItem(f"{item.reorder_level:g} {item.unit}"))
            status = QTableWidgetItem("Low stock" if item.is_low else "In stock")
            status.setForeground(QColor(Color.DANGER if item.is_low else Color.SUCCESS))
            self._table.setItem(r, 3, status)
            self._table.setCellWidget(r, 4, self._actions(item))

    def _actions(self, item) -> QWidget:
        host = QWidget()
        lay = QHBoxLayout(host)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(6)
        edit = make_button("Edit", "secondary")
        edit.clicked.connect(lambda: self._edit(item))
        delete = make_button("Delete", "danger")
        delete.clicked.connect(lambda: self._delete(item))
        for b in (edit, delete):
            b.setMinimumHeight(32)
        lay.addWidget(edit)
        lay.addWidget(delete)
        return host

    def _add(self) -> None:
        def submit(values):
            inventory_service.create_item(values["name"], values["unit"],
                                          values["quantity"], values["reorder"])
        dlg = FormDialog("Add Inventory Item", [
            ("name", "Name", "text", {"placeholder": "e.g. Tomatoes"}),
            ("unit", "Unit", "text", {"value": "unit", "placeholder": "kg, L, pcs…"}),
            ("quantity", "Quantity", "float", {"min": 0.0, "max": 1_000_000.0}),
            ("reorder", "Reorder Level", "float", {"value": 10.0, "min": 0.0, "max": 1_000_000.0}),
        ], submit, self)
        if dlg.exec_():
            self.refresh()

    def _edit(self, item) -> None:
        def submit(values):
            inventory_service.update_item(item.id, values["name"], values["unit"],
                                          values["quantity"], values["reorder"])
        dlg = FormDialog("Edit Inventory Item", [
            ("name", "Name", "text", {"value": item.name}),
            ("unit", "Unit", "text", {"value": item.unit}),
            ("quantity", "Quantity", "float", {"value": item.quantity, "min": 0.0, "max": 1_000_000.0}),
            ("reorder", "Reorder Level", "float", {"value": item.reorder_level, "min": 0.0, "max": 1_000_000.0}),
        ], submit, self)
        if dlg.exec_():
            self.refresh()

    def _delete(self, item) -> None:
        if QMessageBox.question(self, "Delete item", f"Delete '{item.name}'?") == QMessageBox.Yes:
            inventory_service.delete_item(item.id)
            self.refresh()

    def on_show(self) -> None:
        self.refresh()
