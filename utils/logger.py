"""Centralised logging configuration.

Provides a single ``get_logger`` factory that writes rotating daily logs to
the ``logs/`` directory and mirrors output to the console. A global excepthook
ensures uncaught exceptions are always recorded instead of silently crashing.
"""
from __future__ import annotations

import logging
import os
import sys
from datetime import date
from logging.handlers import RotatingFileHandler

from app import config

_CONFIGURED = False


def _configure_root() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    config.ensure_directories()
    log_file = os.path.join(config.LOGS_DIR, f"app_{date.today():%Y-%m-%d}.log")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(console)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for the given module name."""
    _configure_root()
    return logging.getLogger(name)


def install_global_exception_hook() -> None:
    """Route uncaught exceptions to the log file instead of stderr only."""
    logger = get_logger("unhandled")

    def _hook(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_tb))

    sys.excepthook = _hook
