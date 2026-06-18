"""Professional sidebar navigation with icons, active state and hover."""
from __future__ import annotations

from typing import Dict, List, Tuple

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QButtonGroup, QFrame, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget,
)

from app import __app_name__, __version__
from app.theme import Color, Font, Radius
from views.components.icons import make_icon


class NavButton(QPushButton):
    def __init__(self, key: str, label: str, icon: str, parent=None):
        super().__init__(label, parent)
        self.key = key
        self._icon = icon
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(46)
        self.setIcon_(False)
        self.setStyleSheet(self._qss())
        self.toggled.connect(lambda checked: self.setIcon_(checked))

    def setIcon_(self, active: bool) -> None:
        from PyQt5.QtGui import QIcon
        color = Color.TEXT_ON_PRIMARY if active else Color.SIDEBAR_TEXT
        self.setIcon(QIcon(make_icon(self._icon, color, 20)))

    def _qss(self) -> str:
        return f"""
        QPushButton {{
            text-align: left;
            padding: 10px 16px;
            border: none;
            border-radius: {Radius.MD}px;
            color: {Color.SIDEBAR_TEXT};
            background-color: transparent;
            font-size: {Font.BODY}px;
            font-weight: 600;
        }}
        QPushButton:hover {{ background-color: {Color.SIDEBAR_HOVER_BG}; color: #FFFFFF; }}
        QPushButton:checked {{ background-color: {Color.SIDEBAR_ACTIVE_BG}; color: #FFFFFF; }}
        """


class Sidebar(QFrame):
    navigated = pyqtSignal(str)
    logout_requested = pyqtSignal()

    ITEMS: List[Tuple[str, str, str]] = [
        ("dashboard", "Dashboard", "dashboard"),
        ("orders", "Orders", "orders"),
        ("menu", "Menu", "menu"),
        ("customers", "Customers", "customers"),
        ("inventory", "Inventory", "inventory"),
        ("reports", "Reports", "reports"),
        ("settings", "Settings", "settings"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setStyleSheet(f"#Sidebar {{ background-color: {Color.SIDEBAR_BG}; }}")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setFixedWidth(248)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 22, 16, 18)
        layout.setSpacing(6)

        # Brand
        brand = QLabel(__app_name__)
        brand.setWordWrap(True)
        brand.setStyleSheet(
            f"color: #FFFFFF; font-size: {Font.SECTION_HEADER}px; font-weight: 800; padding: 0 6px;"
        )
        tagline = QLabel("Restaurant Manager")
        tagline.setStyleSheet(f"color: {Color.SIDEBAR_TEXT}; font-size: {Font.SMALL}px; padding: 0 6px;")
        layout.addWidget(brand)
        layout.addWidget(tagline)
        layout.addSpacing(18)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: Dict[str, NavButton] = {}
        for key, label, icon in self.ITEMS:
            btn = NavButton(key, label, icon)
            btn.clicked.connect(lambda _=False, k=key: self.navigated.emit(k))
            self._group.addButton(btn)
            self._buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch(1)

        self._user_lbl = QLabel("")
        self._user_lbl.setWordWrap(True)
        self._user_lbl.setStyleSheet(
            f"color: {Color.SIDEBAR_TEXT}; font-size: {Font.SMALL}px; padding: 6px;"
        )
        layout.addWidget(self._user_lbl)

        logout = NavButton("logout", "Logout", "logout")
        logout.setCheckable(False)
        logout.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout)

        version = QLabel(f"v{__version__}")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet(f"color: #475569; font-size: 11px;")
        layout.addWidget(version)

    def set_active(self, key: str) -> None:
        if key in self._buttons:
            self._buttons[key].setChecked(True)

    def set_user(self, name: str, role: str) -> None:
        self._user_lbl.setText(f"Signed in as\n{name}  ·  {role}")
