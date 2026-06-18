"""Dialog for composing a new order (cart builder)."""
from __future__ import annotations

from typing import Dict, List, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel, QMessageBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.config import TAX_RATE
from app.theme import Color, Font
from services.customer_service import customer_service
from services.food_service import food_service
from services.order_service import order_service
from services.table_service import table_service
from utils.exceptions import AppError
from utils.helpers import format_currency
from views.components.widgets import make_button


class NewOrderDialog(QDialog):
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self._user_id = user_id
        self.setWindowTitle("New Order")
        self.setModal(True)
        self.setMinimumSize(620, 560)
        self.setStyleSheet(f"QDialog {{ background-color: {Color.SURFACE}; }}")
        # cart: food_id -> [name, price, qty]
        self._cart: Dict[int, list] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)

        title = QLabel("Create New Order")
        title.setStyleSheet(f"font-size: {Font.SECTION_HEADER}px; font-weight: 700;")
        layout.addWidget(title)

        # table + customer selectors
        selectors = QHBoxLayout()
        self._table_combo = QComboBox()
        self._table_combo.addItem("Takeaway / No table", None)
        for t in table_service.list_tables():
            self._table_combo.addItem(f"{t.name} ({t.status})", t.id)
        self._customer_combo = QComboBox()
        self._customer_combo.addItem("Walk-in", None)
        for c in customer_service.list_customers():
            self._customer_combo.addItem(c.name, c.id)
        for w in (self._table_combo, self._customer_combo):
            w.setMinimumHeight(40)
        selectors.addWidget(self._labeled("Table", self._table_combo), 1)
        selectors.addWidget(self._labeled("Customer", self._customer_combo), 1)
        layout.addLayout(selectors)

        # add-item row
        add_row = QHBoxLayout()
        self._food_combo = QComboBox()
        self._food_combo.setMinimumHeight(40)
        self._foods = food_service.list_foods()
        for f in self._foods:
            if f.is_available:
                self._food_combo.addItem(f"{f.name} — {format_currency(f.price)}", f.id)
        self._qty = QSpinBox()
        self._qty.setRange(1, 99)
        self._qty.setValue(1)
        self._qty.setMinimumHeight(40)
        add_btn = make_button("Add")
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(self._add_to_cart)
        add_row.addWidget(self._food_combo, 1)
        add_row.addWidget(self._qty)
        add_row.addWidget(add_btn)
        layout.addLayout(add_row)

        # cart table
        self._cart_table = QTableWidget(0, 4)
        self._cart_table.setHorizontalHeaderLabels(["Item", "Qty", "Line Total", ""])
        self._cart_table.verticalHeader().setVisible(False)
        self._cart_table.horizontalHeader().setStretchLastSection(False)
        self._cart_table.setColumnWidth(0, 280)
        self._cart_table.setColumnWidth(1, 70)
        self._cart_table.setColumnWidth(2, 120)
        self._cart_table.setColumnWidth(3, 90)
        layout.addWidget(self._cart_table, 1)

        # totals
        self._totals = QLabel("")
        self._totals.setAlignment(Qt.AlignRight)
        self._totals.setStyleSheet(f"font-size: {Font.BODY}px; color: {Color.TEXT_SECONDARY};")
        layout.addWidget(self._totals)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = make_button("Cancel", "secondary")
        cancel.clicked.connect(self.reject)
        place = make_button("Place Order", "success")
        place.clicked.connect(self._place)
        buttons.addWidget(cancel)
        buttons.addWidget(place)
        layout.addLayout(buttons)
        self._render_cart()

    def _labeled(self, text: str, widget: QWidget) -> QWidget:
        host = QWidget()
        col = QVBoxLayout(host)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(4)
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-weight: 600; font-size: {Font.SMALL}px;")
        col.addWidget(lbl)
        col.addWidget(widget)
        return host

    def _add_to_cart(self) -> None:
        food_id = self._food_combo.currentData()
        if food_id is None:
            return
        food = next((f for f in self._foods if f.id == food_id), None)
        if food is None:
            return
        qty = self._qty.value()
        if food_id in self._cart:
            self._cart[food_id][2] += qty
        else:
            self._cart[food_id] = [food.name, food.price, qty]
        self._render_cart()

    def _render_cart(self) -> None:
        self._cart_table.setRowCount(0)
        subtotal = 0.0
        for food_id, (name, price, qty) in self._cart.items():
            line = price * qty
            subtotal += line
            r = self._cart_table.rowCount()
            self._cart_table.insertRow(r)
            self._cart_table.setItem(r, 0, QTableWidgetItem(name))
            self._cart_table.setItem(r, 1, QTableWidgetItem(str(qty)))
            self._cart_table.setItem(r, 2, QTableWidgetItem(format_currency(line)))
            remove = make_button("Remove", "danger")
            remove.setMinimumHeight(30)
            remove.clicked.connect(lambda _=False, fid=food_id: self._remove(fid))
            self._cart_table.setCellWidget(r, 3, remove)
        tax = subtotal * TAX_RATE
        total = subtotal + tax
        self._totals.setText(
            f"Subtotal: {format_currency(subtotal)}    "
            f"Tax ({TAX_RATE*100:.0f}%): {format_currency(tax)}    "
            f"<b style='color:{Color.TEXT_PRIMARY};'>Total: {format_currency(total)}</b>"
        )

    def _remove(self, food_id: int) -> None:
        self._cart.pop(food_id, None)
        self._render_cart()

    def _place(self) -> None:
        if not self._cart:
            QMessageBox.warning(self, "Empty order", "Add at least one item to the order.")
            return
        lines: List[Tuple[int, str, float, int]] = [
            (fid, name, price, qty) for fid, (name, price, qty) in self._cart.items()
        ]
        try:
            order_service.create_order(
                lines, self._table_combo.currentData(),
                self._customer_combo.currentData(), self._user_id,
            )
        except AppError as exc:
            QMessageBox.critical(self, "Could not place order", str(exc))
            return
        self.accept()
