"""A single restaurant table tile for the floor view."""
from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from app.theme import Color, Font, Radius, status_color
from models.table import RestaurantTable


class FloorTable(QWidget):
    """Clickable tile that visualises a table and its status."""

    clicked = pyqtSignal(object)  # emits RestaurantTable

    def __init__(self, table: RestaurantTable, parent=None):
        super().__init__(parent)
        self.table = table
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(120, 110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(4)

        self._name = QLabel(table.name)
        self._name.setStyleSheet(f"font-size: {Font.SECTION_HEADER}px; font-weight: 700;")
        self._seats = QLabel(f"{table.seats} seats")
        self._seats.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: {Font.SMALL}px;")
        self._status = QLabel(table.status)
        self._status.setAlignment(Qt.AlignCenter)

        layout.addWidget(self._name)
        layout.addWidget(self._seats)
        layout.addStretch(1)
        layout.addWidget(self._status)
        self._restyle()

    def _restyle(self) -> None:
        c = status_color(self.table.status)
        self.setStyleSheet(
            f"FloorTable {{ background-color: {Color.SURFACE}; border: 1px solid {Color.BORDER};"
            f" border-left: 4px solid {c}; border-radius: {Radius.MD}px; }}"
            f"FloorTable:hover {{ background-color: {Color.HOVER}; }}"
        )
        self._status.setStyleSheet(
            f"background-color: {c}1A; color: {c}; border-radius: {Radius.SM}px;"
            f" padding: 4px 8px; font-weight: 700; font-size: {Font.SMALL}px;"
        )

    def update_table(self, table: RestaurantTable) -> None:
        self.table = table
        self._name.setText(table.name)
        self._seats.setText(f"{table.seats} seats")
        self._status.setText(table.status)
        self._restyle()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self.rect().contains(event.pos()):
            self.clicked.emit(self.table)
        super().mouseReleaseEvent(event)
