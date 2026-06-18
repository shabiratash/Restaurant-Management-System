"""Customer directory: list, search, add, edit, delete."""
from __future__ import annotations

from PyQt5.QtWidgets import (
    QAbstractItemView, QHBoxLayout, QHeaderView, QLineEdit, QMessageBox,
    QTableWidget, QTableWidgetItem, QWidget,
)

from services.customer_service import customer_service
from utils.logger import get_logger
from views.base_view import BaseView
from views.components.form_dialog import FormDialog
from views.components.widgets import Card, make_button

logger = get_logger(__name__)


class CustomersView(BaseView):
    def __init__(self, parent=None):
        super().__init__("Customers", "Manage your guest directory", scroll=False, parent=parent)
        add_btn = make_button("+ Add Customer")
        add_btn.clicked.connect(self._add)
        self.add_action(add_btn)

        card = Card(padding=18)
        toolbar = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search by name, phone or email…")
        self._search.setMinimumHeight(40)
        self._search.textChanged.connect(self.refresh)
        toolbar.addWidget(self._search, 1)
        card.body().addLayout(toolbar)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Name", "Phone", "Email", "Actions"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._table.setColumnWidth(3, 170)
        self._table.verticalHeader().setDefaultSectionSize(52)
        card.body().addWidget(self._table, 1)
        self.content.addWidget(card, 1)
        self.refresh()

    def refresh(self) -> None:
        try:
            customers = customer_service.list_customers(self._search.text().strip())
        except Exception:
            logger.exception("Failed to load customers")
            customers = []
        self._table.setRowCount(0)
        for c in customers:
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setItem(r, 0, QTableWidgetItem(c.name))
            self._table.setItem(r, 1, QTableWidgetItem(c.phone or "—"))
            self._table.setItem(r, 2, QTableWidgetItem(c.email or "—"))
            self._table.setCellWidget(r, 3, self._actions(c))

    def _actions(self, customer) -> QWidget:
        host = QWidget()
        lay = QHBoxLayout(host)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(6)
        edit = make_button("Edit", "secondary")
        edit.clicked.connect(lambda: self._edit(customer))
        delete = make_button("Delete", "danger")
        delete.clicked.connect(lambda: self._delete(customer))
        for b in (edit, delete):
            b.setMinimumHeight(32)
        lay.addWidget(edit)
        lay.addWidget(delete)
        return host

    def _add(self) -> None:
        def submit(values):
            customer_service.create_customer(values["name"], values["phone"], values["email"])
        dlg = FormDialog("Add Customer", [
            ("name", "Name", "text", {"placeholder": "Full name"}),
            ("phone", "Phone", "text", {"placeholder": "Optional"}),
            ("email", "Email", "text", {"placeholder": "Optional"}),
        ], submit, self)
        if dlg.exec_():
            self.refresh()

    def _edit(self, customer) -> None:
        def submit(values):
            customer_service.update_customer(customer.id, values["name"],
                                             values["phone"], values["email"])
        dlg = FormDialog("Edit Customer", [
            ("name", "Name", "text", {"value": customer.name}),
            ("phone", "Phone", "text", {"value": customer.phone}),
            ("email", "Email", "text", {"value": customer.email}),
        ], submit, self)
        if dlg.exec_():
            self.refresh()

    def _delete(self, customer) -> None:
        if QMessageBox.question(self, "Delete customer",
                                f"Delete '{customer.name}'?") == QMessageBox.Yes:
            customer_service.delete_customer(customer.id)
            self.refresh()

    def on_show(self) -> None:
        self.refresh()
