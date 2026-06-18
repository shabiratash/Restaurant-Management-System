"""Premium light theme: color palette, typography, spacing and global QSS.

This is the single source of truth for the application's visual language.
Views must consume these tokens instead of hardcoding colors so the look stays
consistent and is trivial to retheme.
"""
from __future__ import annotations


class Color:
    """Design-system color tokens (light theme only)."""

    BACKGROUND = "#F8FAFC"
    SURFACE = "#FFFFFF"

    PRIMARY = "#2563EB"
    PRIMARY_HOVER = "#1D4ED8"
    PRIMARY_SOFT = "#EFF6FF"

    SUCCESS = "#16A34A"
    SUCCESS_SOFT = "#DCFCE7"
    WARNING = "#F59E0B"
    WARNING_SOFT = "#FEF3C7"
    DANGER = "#DC2626"
    DANGER_SOFT = "#FEE2E2"

    TEXT_PRIMARY = "#0F172A"
    TEXT_SECONDARY = "#64748B"
    TEXT_ON_PRIMARY = "#FFFFFF"

    BORDER = "#E2E8F0"
    HOVER = "#F1F5F9"

    SIDEBAR_BG = "#0F172A"
    SIDEBAR_TEXT = "#CBD5E1"
    SIDEBAR_ACTIVE_BG = "#2563EB"
    SIDEBAR_HOVER_BG = "#1E293B"


class Font:
    """Typography tokens."""

    FAMILY = "Segoe UI"
    PAGE_TITLE = 24
    SECTION_HEADER = 18
    BODY = 14
    SMALL = 12
    BUTTON = 14


class Radius:
    SM = 6
    MD = 10
    LG = 16


def status_color(status: str) -> str:
    """Map a domain status string to a semantic color."""
    mapping = {
        "Available": Color.SUCCESS,
        "Reserved": Color.WARNING,
        "Occupied": Color.DANGER,
        "Pending": Color.WARNING,
        "Preparing": Color.PRIMARY,
        "Ready": Color.SUCCESS,
        "Served": Color.TEXT_SECONDARY,
        "Cancelled": Color.DANGER,
    }
    return mapping.get(status, Color.TEXT_SECONDARY)


def global_stylesheet() -> str:
    """Return the application-wide QSS stylesheet."""
    return f"""
    * {{
        font-family: "{Font.FAMILY}";
        font-size: {Font.BODY}px;
        color: {Color.TEXT_PRIMARY};
        outline: none;
    }}

    QWidget#AppRoot, QMainWindow {{
        background-color: {Color.BACKGROUND};
    }}

    QToolTip {{
        background-color: {Color.TEXT_PRIMARY};
        color: #FFFFFF;
        border: none;
        padding: 6px 8px;
        border-radius: {Radius.SM}px;
    }}

    /* ---- Cards / surfaces ---- */
    QFrame#Card, QFrame#Surface {{
        background-color: {Color.SURFACE};
        border: 1px solid {Color.BORDER};
        border-radius: {Radius.LG}px;
    }}

    /* ---- Buttons ---- */
    QPushButton {{
        background-color: {Color.PRIMARY};
        color: {Color.TEXT_ON_PRIMARY};
        border: none;
        border-radius: {Radius.MD}px;
        padding: 10px 18px;
        font-size: {Font.BUTTON}px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background-color: {Color.PRIMARY_HOVER}; }}
    QPushButton:disabled {{ background-color: #93C5FD; color: #E0E7FF; }}

    QPushButton[variant="secondary"] {{
        background-color: {Color.SURFACE};
        color: {Color.TEXT_PRIMARY};
        border: 1px solid {Color.BORDER};
    }}
    QPushButton[variant="secondary"]:hover {{ background-color: {Color.HOVER}; }}

    QPushButton[variant="danger"] {{ background-color: {Color.DANGER}; }}
    QPushButton[variant="danger"]:hover {{ background-color: #B91C1C; }}

    QPushButton[variant="success"] {{ background-color: {Color.SUCCESS}; }}
    QPushButton[variant="success"]:hover {{ background-color: #15803D; }}

    QPushButton[variant="ghost"] {{
        background-color: transparent;
        color: {Color.TEXT_SECONDARY};
        padding: 6px 10px;
    }}
    QPushButton[variant="ghost"]:hover {{ background-color: {Color.HOVER}; }}

    /* ---- Inputs ---- */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QPlainTextEdit, QTextEdit {{
        background-color: {Color.SURFACE};
        border: 1px solid {Color.BORDER};
        border-radius: {Radius.MD}px;
        padding: 9px 12px;
        selection-background-color: {Color.PRIMARY_SOFT};
        selection-color: {Color.TEXT_PRIMARY};
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
    QDateEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
        border: 1px solid {Color.PRIMARY};
    }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{
        background-color: {Color.SURFACE};
        border: 1px solid {Color.BORDER};
        selection-background-color: {Color.PRIMARY_SOFT};
        selection-color: {Color.TEXT_PRIMARY};
        outline: none;
    }}

    /* ---- Tables ---- */
    QTableWidget, QTableView {{
        background-color: {Color.SURFACE};
        border: 1px solid {Color.BORDER};
        border-radius: {Radius.MD}px;
        gridline-color: {Color.BORDER};
        selection-background-color: {Color.PRIMARY_SOFT};
        selection-color: {Color.TEXT_PRIMARY};
    }}
    QHeaderView::section {{
        background-color: {Color.BACKGROUND};
        color: {Color.TEXT_SECONDARY};
        padding: 10px;
        border: none;
        border-bottom: 1px solid {Color.BORDER};
        font-weight: 600;
    }}
    QTableWidget::item {{ padding: 6px; }}

    /* ---- Scrollbars ---- */
    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: #CBD5E1; border-radius: 5px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: #94A3B8; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
    QScrollBar::handle:horizontal {{ background: #CBD5E1; border-radius: 5px; min-width: 30px; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
    QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

    /* ---- Misc ---- */
    QCheckBox {{ color: {Color.TEXT_SECONDARY}; spacing: 8px; }}
    QCheckBox::indicator {{ width: 18px; height: 18px; border: 1px solid {Color.BORDER};
        border-radius: 5px; background: {Color.SURFACE}; }}
    QCheckBox::indicator:checked {{ background: {Color.PRIMARY}; border-color: {Color.PRIMARY}; }}

    QLabel[role="pageTitle"] {{ font-size: {Font.PAGE_TITLE}px; font-weight: 700; color: {Color.TEXT_PRIMARY}; }}
    QLabel[role="sectionHeader"] {{ font-size: {Font.SECTION_HEADER}px; font-weight: 600; color: {Color.TEXT_PRIMARY}; }}
    QLabel[role="muted"] {{ color: {Color.TEXT_SECONDARY}; }}
    """
