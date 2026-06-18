"""Premium KPI metric card with icon, value and trend indicator."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from app.theme import Color, Font, Radius
from views.components.icons import make_icon
from views.components.widgets import Card, bold_value


class KpiCard(Card):
    def __init__(self, title: str, icon: str, accent: str = Color.PRIMARY, parent=None):
        super().__init__(parent, padding=22)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(190)
        self._accent = accent

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"color: {Color.TEXT_SECONDARY}; font-size: {Font.BODY}px; font-weight: 600;"
        )
        top.addWidget(title_lbl)
        top.addStretch(1)

        icon_holder = QLabel()
        icon_holder.setPixmap(make_icon(icon, accent, 22))
        icon_holder.setFixedSize(40, 40)
        icon_holder.setAlignment(Qt.AlignCenter)
        icon_holder.setStyleSheet(
            f"background-color: {accent}1A; border-radius: {Radius.MD}px;"
        )
        top.addWidget(icon_holder)
        self.body().addLayout(top)

        self._value = bold_value("—", 26)
        self.body().addWidget(self._value)

        self._trend = QLabel("")
        self._trend.setStyleSheet(f"font-size: {Font.SMALL}px; font-weight: 600;")
        self.body().addWidget(self._trend)
        self.body().addStretch(1)

    def set_value(self, value: str) -> None:
        self._value.setText(value)

    def set_trend(self, current: float, previous: float, *, suffix: str = "vs yesterday") -> None:
        if previous <= 0:
            if current > 0:
                self._trend.setText(f"▲ new activity  ·  {suffix}")
                self._trend.setStyleSheet(
                    f"color: {Color.SUCCESS}; font-size: {Font.SMALL}px; font-weight: 600;"
                )
            else:
                self._trend.setText(f"no change  ·  {suffix}")
                self._trend.setStyleSheet(
                    f"color: {Color.TEXT_SECONDARY}; font-size: {Font.SMALL}px; font-weight: 600;"
                )
            return
        pct = (current - previous) / previous * 100
        up = pct >= 0
        color = Color.SUCCESS if up else Color.DANGER
        arrow = "▲" if up else "▼"
        self._trend.setText(f"{arrow} {abs(pct):.1f}%  ·  {suffix}")
        self._trend.setStyleSheet(
            f"color: {color}; font-size: {Font.SMALL}px; font-weight: 600;"
        )

    def set_subtitle(self, text: str) -> None:
        self._trend.setText(text)
        self._trend.setStyleSheet(
            f"color: {Color.TEXT_SECONDARY}; font-size: {Font.SMALL}px; font-weight: 600;"
        )
