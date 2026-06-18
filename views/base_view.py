"""Base class for full-page feature views.

Provides a consistent page header (title + subtitle + right-aligned actions)
and a scrollable content area so every page is responsive by default.
"""
from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget,
)

from app.theme import Color, Font


class BaseView(QWidget):
    def __init__(self, title: str, subtitle: str = "", *, scroll: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("AppRoot")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(12)
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self._title = QLabel(title)
        self._title.setProperty("role", "pageTitle")
        text_col.addWidget(self._title)
        self._subtitle = QLabel(subtitle)
        self._subtitle.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: {Font.BODY}px;")
        self._subtitle.setVisible(bool(subtitle))
        text_col.addWidget(self._subtitle)
        header.addLayout(text_col)
        header.addStretch(1)

        self._actions_layout = QHBoxLayout()
        self._actions_layout.setSpacing(10)
        header.addLayout(self._actions_layout)
        outer.addLayout(header)

        if scroll:
            area = QScrollArea()
            area.setWidgetResizable(True)
            area.setFrameShape(QFrame.NoFrame)
            self._content_host = QWidget()
            self._content = QVBoxLayout(self._content_host)
            self._content.setContentsMargins(0, 0, 0, 0)
            self._content.setSpacing(18)
            area.setWidget(self._content_host)
            outer.addWidget(area, 1)
        else:
            host = QWidget()
            self._content = QVBoxLayout(host)
            self._content.setContentsMargins(0, 0, 0, 0)
            self._content.setSpacing(18)
            outer.addWidget(host, 1)

    @property
    def content(self) -> QVBoxLayout:
        return self._content

    def add_action(self, widget: QWidget) -> None:
        self._actions_layout.addWidget(widget)

    def set_subtitle(self, text: str) -> None:
        self._subtitle.setText(text)
        self._subtitle.setVisible(bool(text))

    def on_show(self) -> None:
        """Hook called whenever the page becomes visible. Override to refresh."""
