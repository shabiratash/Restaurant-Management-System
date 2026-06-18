"""Responsive split-screen login experience.

Layout rules honoured:
  * Built entirely with layouts + stretch factors.
  * No setGeometry / setFixedWidth / setFixedHeight.
  * The branding panel collapses automatically on narrow widths so the form
    stays readable from 1280x720 up to 2560x1440.
"""
from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget,
)

from app import __app_name__
from app.theme import Color, Font, Radius
from services.auth_service import auth_service
from utils.exceptions import AppError
from utils.logger import get_logger
from views.components.icons import make_icon
from views.components.widgets import Card, make_button

logger = get_logger(__name__)


class LoginView(QWidget):
    logged_in = pyqtSignal(object)  # emits the authenticated User

    # Below this width the branding panel is hidden to protect readability.
    COLLAPSE_WIDTH = 920

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AppRoot")
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._branding = self._build_branding()
        right = self._build_form_panel()

        root.addWidget(self._branding, 6)
        root.addWidget(right, 5)

    # -- branding (left) -----------------------------------------------
    def _build_branding(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Branding")
        panel.setStyleSheet(
            f"""#Branding {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Color.PRIMARY}, stop:1 #1E3A8A);
            }}"""
        )
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(64, 64, 64, 64)
        layout.setSpacing(18)
        layout.addStretch(1)

        logo = QLabel()
        logo.setPixmap(make_icon("menu", "#FFFFFF", 56))
        layout.addWidget(logo)

        title = QLabel(__app_name__)
        title.setWordWrap(True)
        title.setStyleSheet("color: #FFFFFF; font-size: 40px; font-weight: 800;")
        layout.addWidget(title)

        welcome = QLabel("Run your restaurant with confidence.")
        welcome.setWordWrap(True)
        welcome.setStyleSheet("color: #DBEAFE; font-size: 20px; font-weight: 600;")
        layout.addWidget(welcome)

        desc = QLabel(
            "A complete point-of-sale and management suite — live floor plans, "
            "real-time orders, menu and inventory control, and sales analytics, "
            "all in one elegant workspace."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #BFDBFE; font-size: 15px; line-height: 150%;")
        layout.addWidget(desc)

        layout.addSpacing(14)
        for feature in ("Live restaurant floor view", "Real-time order feed",
                        "Sales & inventory analytics"):
            row = QHBoxLayout()
            dot = QLabel()
            dot.setPixmap(make_icon("plus", "#FFFFFF", 16))
            text = QLabel(feature)
            text.setStyleSheet("color: #EFF6FF; font-size: 14px; font-weight: 600;")
            row.addWidget(dot)
            row.addWidget(text)
            row.addStretch(1)
            layout.addLayout(row)

        layout.addStretch(2)
        return panel

    # -- form (right) ---------------------------------------------------
    def _build_form_panel(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background-color: {Color.BACKGROUND};")

        container = QWidget()
        container.setStyleSheet(f"background-color: {Color.BACKGROUND};")
        outer = QVBoxLayout(container)
        outer.setContentsMargins(32, 32, 32, 32)

        outer.addStretch(1)
        center_row = QHBoxLayout()
        center_row.addStretch(1)

        card = Card(padding=36)
        card.setMaximumWidth(440)
        card.setMinimumWidth(320)
        card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        body = card.body()
        body.setSpacing(14)

        heading = QLabel("Welcome back")
        heading.setStyleSheet(f"font-size: 26px; font-weight: 800; color: {Color.TEXT_PRIMARY};")
        subtitle = QLabel("Sign in to your account to continue")
        subtitle.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: {Font.BODY}px;")
        body.addWidget(heading)
        body.addWidget(subtitle)
        body.addSpacing(8)

        body.addWidget(self._field_label("Username"))
        self._username = QLineEdit()
        self._username.setPlaceholderText("Enter your username")
        self._username.setMinimumHeight(44)
        body.addWidget(self._username)

        body.addWidget(self._field_label("Password"))
        pw_row = QHBoxLayout()
        pw_row.setSpacing(8)
        self._password = QLineEdit()
        self._password.setPlaceholderText("Enter your password")
        self._password.setEchoMode(QLineEdit.Password)
        self._password.setMinimumHeight(44)
        self._password.returnPressed.connect(self._attempt_login)
        self._toggle = make_button("Show", "secondary")
        self._toggle.setCheckable(True)
        self._toggle.setMinimumHeight(44)
        self._toggle.setMaximumWidth(78)
        self._toggle.toggled.connect(self._toggle_password)
        pw_row.addWidget(self._password, 1)
        pw_row.addWidget(self._toggle)
        body.addLayout(pw_row)

        options = QHBoxLayout()
        self._remember = QCheckBox("Remember me")
        options.addWidget(self._remember)
        options.addStretch(1)
        body.addLayout(options)

        self._error = QLabel("")
        self._error.setWordWrap(True)
        self._error.setStyleSheet(
            f"color: {Color.DANGER}; background-color: {Color.DANGER_SOFT};"
            f" border-radius: {Radius.SM}px; padding: 8px 10px; font-size: {Font.SMALL}px;"
        )
        self._error.hide()
        body.addWidget(self._error)

        self._login_btn = make_button("Sign In")
        self._login_btn.setMinimumHeight(46)
        self._login_btn.clicked.connect(self._attempt_login)
        body.addWidget(self._login_btn)

        hint = QLabel("Demo: admin / admin123  ·  manager / manager123  ·  cashier / cashier123")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"color: {Color.TEXT_SECONDARY}; font-size: 11px;")
        body.addSpacing(4)
        body.addWidget(hint)

        center_row.addWidget(card, 2)
        center_row.addStretch(1)
        outer.addLayout(center_row)
        outer.addStretch(1)

        scroll.setWidget(container)
        return scroll

    def _field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            f"color: {Color.TEXT_PRIMARY}; font-size: {Font.SMALL}px; font-weight: 700;"
        )
        return label

    # -- behaviour ------------------------------------------------------
    def _toggle_password(self, checked: bool) -> None:
        self._password.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self._toggle.setText("Hide" if checked else "Show")

    def _attempt_login(self) -> None:
        self._error.hide()
        try:
            user = auth_service.login(self._username.text(), self._password.text())
        except AppError as exc:
            self._show_error(str(exc))
            return
        except Exception:  # pragma: no cover - defensive
            logger.exception("Unexpected login error")
            self._show_error("An unexpected error occurred. Please try again.")
            return
        self._password.clear()
        self.logged_in.emit(user)

    def _show_error(self, message: str) -> None:
        self._error.setText(message)
        self._error.show()

    def focus_username(self) -> None:
        self._username.setFocus()

    # -- responsiveness -------------------------------------------------
    def resizeEvent(self, event) -> None:
        self._branding.setVisible(self.width() >= self.COLLAPSE_WIDTH)
        super().resizeEvent(event)
