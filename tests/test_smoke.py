"""Headless smoke test: bootstrap, build every view, exercise core flows.

Run directly (``python tests/test_smoke.py``) or via pytest. Uses Qt's
offscreen platform so it works without a display.
"""
import os
import sys
import traceback

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Ensure project root is importable when run directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication

import main
from app.theme import global_stylesheet
from services.auth_service import auth_service
from services.food_service import food_service
from services.order_service import order_service


def test_application_smoke():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(global_stylesheet())
    main.bootstrap()

    from views.main_window import MainWindow
    w = MainWindow()
    w.show()
    app.processEvents()

    auth_service.login("admin", "admin123")
    w._on_login(auth_service.current_user)
    app.processEvents()

    for key in ["dashboard", "orders", "menu", "customers", "inventory", "reports", "settings"]:
        w._shell.navigate(key)
        app.processEvents()

    foods = food_service.list_foods()
    assert foods, "Seed data should provide menu items"
    oid = order_service.create_order(
        [(foods[0].id, foods[0].name, foods[0].price, 2)], None, None, 1)
    order_service.update_status(oid, "Served")

    for size in [(1280, 720), (1366, 768), (1920, 1080), (2560, 1440), (1100, 700)]:
        w.resize(*size)
        app.processEvents()

    w._on_logout()
    app.processEvents()


if __name__ == "__main__":
    try:
        test_application_smoke()
    except Exception:
        traceback.print_exc()
        sys.exit(2)
    print("SMOKE OK")
