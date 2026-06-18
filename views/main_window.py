"""Top-level application window: login gate + sidebar-driven app shell."""
from __future__ import annotations

from PyQt5.QtWidgets import (
    QHBoxLayout, QMainWindow, QMessageBox, QStackedWidget, QWidget,
)

from app import __app_name__
from services.auth_service import auth_service
from utils.logger import get_logger
from views.components.sidebar import Sidebar
from views.customers_view import CustomersView
from views.dashboard_view import DashboardView
from views.inventory_view import InventoryView
from views.login_view import LoginView
from views.menu_view import MenuView
from views.orders_view import OrdersView
from views.reports_view import ReportsView
from views.settings_view import SettingsView

logger = get_logger(__name__)


class AppShell(QWidget):
    """Sidebar + stacked feature pages (shown after authentication)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AppRoot")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.navigated.connect(self.navigate)
        self.sidebar.logout_requested.connect(self._request_logout)
        layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self._pages = {
            "dashboard": DashboardView(),
            "orders": OrdersView(),
            "menu": MenuView(),
            "customers": CustomersView(),
            "inventory": InventoryView(),
            "reports": ReportsView(),
            "settings": SettingsView(),
        }
        self._order = list(self._pages.keys())
        for page in self._pages.values():
            self.stack.addWidget(page)

        self.logout_callback = None

    def navigate(self, key: str) -> None:
        if key not in self._pages:
            return
        page = self._pages[key]
        self.stack.setCurrentWidget(page)
        self.sidebar.set_active(key)
        if hasattr(page, "on_show"):
            page.on_show()

    def start(self) -> None:
        user = auth_service.current_user
        if user:
            self.sidebar.set_user(user.full_name, user.role)
        self.navigate("dashboard")

    def _request_logout(self) -> None:
        if QMessageBox.question(self, "Log out", "Are you sure you want to log out?") == QMessageBox.Yes:
            if self.logout_callback:
                self.logout_callback()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(__app_name__)
        self.setMinimumSize(1024, 680)
        self.resize(1366, 820)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._login = LoginView()
        self._login.logged_in.connect(self._on_login)
        self._stack.addWidget(self._login)

        self._shell: AppShell | None = None
        self._login.focus_username()

    def _on_login(self, user) -> None:
        logger.info("Building app shell for %s", user.username)
        self._shell = AppShell()
        self._shell.logout_callback = self._on_logout
        self._stack.addWidget(self._shell)
        self._stack.setCurrentWidget(self._shell)
        self._shell.start()

    def _on_logout(self) -> None:
        auth_service.logout()
        if self._shell is not None:
            self._stack.setCurrentWidget(self._login)
            old = self._shell
            self._shell = None
            self._stack.removeWidget(old)
            old.deleteLater()
        self._login.focus_username()
