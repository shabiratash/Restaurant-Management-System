"""Settings: account info, floor/table management and app details."""
from __future__ import annotations

from PyQt5.QtWidgets import (
    QAbstractItemView, QHBoxLayout, QHeaderView, QLabel, QMessageBox,
    QTableWidget, QTableWidgetItem, QWidget,
)

from app import __app_name__, __version__
from app.config import CURRENCY_SYMBOL, TAX_RATE
from app.theme import Color, Font
from services.auth_service import auth_service
from services.table_service import table_service
from utils.logger import get_logger
from views.base_view import BaseView
from views.components.form_dialog import FormDialog
from views.components.widgets import Card, heading, make_button, muted

logger = get_logger(__name__)


class SettingsView(BaseView):
    def __init__(self, parent=None):
        super().__init__("Settings", "Account, floor and application configuration", parent=parent)
        self._build_account()
        self._build_tables()
        self._build_about()
        self.refresh()

    def _build_account(self) -> None:
        card = Card()
        card.body().addWidget(heading("Account"))
        self._account = QLabel("")
        self._account.setStyleSheet(f"font-size: {Font.BODY}px;")
        card.body().addWidget(self._account)
        card.body().addWidget(muted("Roles control access: Admin, Manager, Cashier."))
        self.content.addWidget(card)

    def _build_tables(self) -> None:
        card = Card(padding=18)
        head = QHBoxLayout()
        head.addWidget(heading("Restaurant Tables"))
        head.addStretch(1)
        add = make_button("+ Add Table")
        add.clicked.connect(self._add_table)
        head.addWidget(add)
        card.body().addLayout(head)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Name", "Seats", "Status", "Actions"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for c in (1, 2, 3):
            header.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self._table.setColumnWidth(3, 120)
        self._table.setMinimumHeight(260)
        self._table.verticalHeader().setDefaultSectionSize(48)
        card.body().addWidget(self._table)
        self.content.addWidget(card)

    def _build_about(self) -> None:
        card = Card()
        card.body().addWidget(heading("About"))
        info = QLabel(
            f"<b>{__app_name__}</b> v{__version__}<br>"
            f"Currency: {CURRENCY_SYMBOL} &nbsp;·&nbsp; Tax rate: {TAX_RATE*100:.0f}%<br>"
            "A premium, fully-responsive PyQt5 restaurant management suite."
        )
        info.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: {Font.BODY}px;")
        info.setWordWrap(True)
        card.body().addWidget(info)
        self.content.addWidget(card)
        self.content.addStretch(1)

    def refresh(self) -> None:
        user = auth_service.current_user
        if user:
            self._account.setText(
                f"<b>{user.full_name}</b><br>Username: {user.username}<br>Role: {user.role}"
            )
        try:
            tables = table_service.list_tables()
        except Exception:
            logger.exception("Failed to load tables")
            tables = []
        self._table.setRowCount(0)
        for t in tables:
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setItem(r, 0, QTableWidgetItem(t.name))
            self._table.setItem(r, 1, QTableWidgetItem(str(t.seats)))
            self._table.setItem(r, 2, QTableWidgetItem(t.status))
            delete = make_button("Delete", "danger")
            delete.setMinimumHeight(30)
            delete.clicked.connect(lambda _=False, tid=t.id, name=t.name: self._delete_table(tid, name))
            host = QWidget()
            lay = QHBoxLayout(host)
            lay.setContentsMargins(6, 4, 6, 4)
            lay.addWidget(delete)
            self._table.setCellWidget(r, 3, host)

    def _add_table(self) -> None:
        def submit(values):
            table_service.create_table(values["name"], values["seats"])
        dlg = FormDialog("Add Table", [
            ("name", "Table name", "text", {"placeholder": "e.g. Table 13"}),
            ("seats", "Seats", "int", {"value": 4, "min": 1, "max": 30}),
        ], submit, self)
        if dlg.exec_():
            self.refresh()

    def _delete_table(self, table_id: int, name: str) -> None:
        if QMessageBox.question(self, "Delete table", f"Delete '{name}'?") == QMessageBox.Yes:
            table_service.delete_table(table_id)
            self.refresh()

    def on_show(self) -> None:
        self.refresh()
