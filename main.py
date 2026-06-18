"""Application entry point for the Restaurant Management System.

Boots the runtime: high-DPI setup, theming, database initialisation and
seeding, global error handling, then launches the main window.
"""
from __future__ import annotations

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMessageBox

# Enable High-DPI scaling before the QApplication is created.
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

from app import __app_name__, config
from app.theme import Font, global_stylesheet
from database.schema import initialize_schema
from database.seed import seed
from utils.logger import get_logger, install_global_exception_hook

logger = get_logger("main")


def bootstrap() -> None:
    """Prepare directories and the database before the UI starts."""
    config.ensure_directories()
    initialize_schema()
    seed()


def main() -> int:
    install_global_exception_hook()
    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setFont(QFont(Font.FAMILY, Font.BODY - 4 if Font.BODY > 10 else Font.BODY))
    app.setStyleSheet(global_stylesheet())

    try:
        bootstrap()
    except Exception as exc:  # pragma: no cover - startup guard
        logger.exception("Fatal error during startup")
        QMessageBox.critical(None, "Startup Error",
                             f"The application could not start:\n\n{exc}")
        return 1

    # Imported after bootstrap so DB-dependent widgets initialise cleanly.
    from views.main_window import MainWindow

    window = MainWindow()
    window.show()
    logger.info("%s started", __app_name__)
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
