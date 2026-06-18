"""Small composable widget helpers shared across views."""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)
from PyQt5.QtGui import QColor, QFont

from app.theme import Color, Font, Radius


def apply_shadow(widget: QWidget, blur: int = 24, y: int = 6, alpha: int = 28) -> None:
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setXOffset(0)
    effect.setYOffset(y)
    effect.setColor(QColor(15, 23, 42, alpha))
    widget.setGraphicsEffect(effect)


class Card(QFrame):
    """A white rounded surface with a subtle shadow."""

    def __init__(self, parent: QWidget | None = None, *, padding: int = 20, shadow: bool = True):
        super().__init__(parent)
        self.setObjectName("Card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(padding, padding, padding, padding)
        self._layout.setSpacing(14)
        if shadow:
            apply_shadow(self)

    def body(self) -> QVBoxLayout:
        return self._layout


def heading(text: str, role: str = "sectionHeader") -> QLabel:
    label = QLabel(text)
    label.setProperty("role", role)
    return label


def muted(text: str, size: int = Font.SMALL) -> QLabel:
    label = QLabel(text)
    label.setProperty("role", "muted")
    f = label.font()
    f.setPointSizeF(size * 0.75)
    label.setFont(f)
    return label


def make_button(text: str, variant: str = "primary") -> QPushButton:
    btn = QPushButton(text)
    if variant != "primary":
        btn.setProperty("variant", variant)
    btn.setCursor(Qt.PointingHandCursor)
    return btn


class Badge(QLabel):
    """A colored status pill."""

    def __init__(self, text: str, color: str, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.set_status(text, color)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

    def set_status(self, text: str, color: str) -> None:
        self.setText(text)
        self.setStyleSheet(
            f"background-color: {color}1A; color: {color}; border-radius: {Radius.SM}px;"
            f" padding: 4px 12px; font-weight: 600; font-size: {Font.SMALL}px;"
        )


def hline() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color: {Color.BORDER}; background: {Color.BORDER}; max-height: 1px;")
    return line


def row(*widgets, spacing: int = 12, stretch_last: bool = False) -> QWidget:
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(spacing)
    for i, w in enumerate(widgets):
        layout.addWidget(w)
        if stretch_last and i == len(widgets) - 1:
            layout.setStretchFactor(w, 1)
    return container


def bold_value(text: str, size: int = 28) -> QLabel:
    label = QLabel(text)
    font = QFont(Font.FAMILY, size)
    font.setWeight(QFont.Bold)
    label.setFont(font)
    label.setStyleSheet(f"color: {Color.TEXT_PRIMARY};")
    return label
