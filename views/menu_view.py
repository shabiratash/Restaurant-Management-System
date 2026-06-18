"""Menu management: list, search, add, edit and remove food items."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView, QHBoxLayout, QHeaderView, QLineEdit, QMessageBox,
    QTableWidget, QTableWidgetItem, QWidget,
)

from app.theme import Color, Font
from services.food_service import food_service
from utils.helpers import format_currency
from utils.logger import get_logger
from views.base_view import BaseView
from views.components.form_dialog import FormDialog
from views.components.widgets import Card, make_button

logger = get_logger(__name__)


class MenuView(BaseView):
    def __init__(self, parent=None):
        super().__init__("Menu", "Manage your food items and pricing", scroll=False, parent=parent)
        add_btn = make_button("+ Add Item")
        add_btn.clicked.connect(self._add)
        self.add_action(add_btn)

        card = Card(padding=18)
        toolbar = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search menu items…")
        self._search.setMinimumHeight(40)
        self._search.textChanged.connect(self.refresh)
        toolbar.addWidget(self._search, 1)
        card.body().addLayout(toolbar)

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["Name", "Category", "Price", "Available", "Actions"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self._table.setColumnWidth(4, 170)
        self._table.verticalHeader().setDefaultSectionSize(52)
        card.body().addWidget(self._table, 1)
        self.content.addWidget(card, 1)
        self.refresh()

    def _category_options(self):
        opts = [("Uncategorised", None)]
        opts += [(c.name, c.id) for c in food_service.list_categories()]
        return opts

    def refresh(self) -> None:
        try:
            foods = food_service.list_foods(self._search.text().strip())
        except Exception:
            logger.exception("Failed to load menu")
            foods = []
        self._table.setRowCount(0)
        for food in foods:
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setItem(r, 0, QTableWidgetItem(food.name))
            self._table.setItem(r, 1, QTableWidgetItem(food.category_name or "—"))
            price_item = QTableWidgetItem(format_currency(food.price))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._table.setItem(r, 2, price_item)
            avail = QTableWidgetItem("Yes" if food.is_available else "No")
            avail.setForeground(Qt.green if food.is_available else Qt.gray)
            self._table.setItem(r, 3, avail)
            self._table.setCellWidget(r, 4, self._actions(food))

    def _actions(self, food) -> QWidget:
        host = QWidget()
        lay = QHBoxLayout(host)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(6)
        edit = make_button("Edit", "secondary")
        edit.clicked.connect(lambda: self._edit(food))
        delete = make_button("Delete", "danger")
        delete.clicked.connect(lambda: self._delete(food))
        for b in (edit, delete):
            b.setMinimumHeight(32)
        lay.addWidget(edit)
        lay.addWidget(delete)
        return host

    def _add(self) -> None:
        def submit(values):
            food_service.create_food(values["name"], values["price"],
                                     values["category_id"], values["available"])
        dlg = FormDialog("Add Menu Item", [
            ("name", "Name", "text", {"placeholder": "e.g. Margherita Pizza"}),
            ("category_id", "Category", "combo", {"options": self._category_options()}),
            ("price", "Price", "float", {"min": 0.0, "max": 9999.0}),
            ("available", "Available", "check", {"text": "Available to order", "value": True}),
        ], submit, self)
        if dlg.exec_():
            self.refresh()

    def _edit(self, food) -> None:
        def submit(values):
            food_service.update_food(food.id, values["name"], values["price"],
                                     values["category_id"], values["available"])
        dlg = FormDialog("Edit Menu Item", [
            ("name", "Name", "text", {"value": food.name}),
            ("category_id", "Category", "combo",
             {"options": self._category_options(), "value": food.category_id}),
            ("price", "Price", "float", {"value": food.price, "min": 0.0, "max": 9999.0}),
            ("available", "Available", "check", {"text": "Available to order", "value": food.is_available}),
        ], submit, self)
        if dlg.exec_():
            self.refresh()

    def _delete(self, food) -> None:
        if QMessageBox.question(self, "Delete item",
                                f"Delete '{food.name}' from the menu?") == QMessageBox.Yes:
            food_service.delete_food(food.id)
            self.refresh()

    def on_show(self) -> None:
        self.refresh()
