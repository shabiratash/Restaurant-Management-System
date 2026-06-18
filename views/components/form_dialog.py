"""A reusable, validated form dialog.

Declaratively build a modal form from field specs. Returns cleaned values on
accept; validation errors raised by the on_submit callback are shown inline
instead of crashing.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QVBoxLayout, QWidget,
)

from app.theme import Color, Font, Radius
from utils.exceptions import AppError
from views.components.widgets import make_button

# Field spec: (key, label, type, config)
FieldSpec = Tuple[str, str, str, dict]


class FormDialog(QDialog):
    def __init__(self, title: str, fields: Sequence[FieldSpec],
                 on_submit: Callable[[Dict[str, Any]], None],
                 parent: Optional[QWidget] = None, submit_text: str = "Save"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet(f"QDialog {{ background-color: {Color.SURFACE}; }}")
        self._on_submit = on_submit
        self._widgets: Dict[str, QWidget] = {}
        self._types: Dict[str, str] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(16)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: {Font.SECTION_HEADER}px; font-weight: 700;")
        layout.addWidget(title_lbl)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft)
        for key, label, ftype, cfg in fields:
            widget = self._make_widget(ftype, cfg)
            self._widgets[key] = widget
            self._types[key] = ftype
            lbl = QLabel(label)
            lbl.setStyleSheet(f"font-weight: 600; font-size: {Font.SMALL}px;")
            form.addRow(lbl, widget)
        layout.addLayout(form)

        self._error = QLabel("")
        self._error.setWordWrap(True)
        self._error.setStyleSheet(
            f"color: {Color.DANGER}; background-color: {Color.DANGER_SOFT};"
            f" border-radius: {Radius.SM}px; padding: 8px 10px; font-size: {Font.SMALL}px;"
        )
        self._error.hide()
        layout.addWidget(self._error)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = make_button("Cancel", "secondary")
        cancel.clicked.connect(self.reject)
        submit = make_button(submit_text)
        submit.clicked.connect(self._submit)
        buttons.addWidget(cancel)
        buttons.addWidget(submit)
        layout.addLayout(buttons)

    def _make_widget(self, ftype: str, cfg: dict) -> QWidget:
        if ftype == "text":
            w = QLineEdit()
            w.setText(str(cfg.get("value", "")))
            if cfg.get("placeholder"):
                w.setPlaceholderText(cfg["placeholder"])
            w.setMinimumHeight(40)
            return w
        if ftype == "int":
            w = QSpinBox()
            w.setRange(cfg.get("min", 0), cfg.get("max", 1_000_000))
            w.setValue(int(cfg.get("value", 0)))
            w.setMinimumHeight(40)
            return w
        if ftype == "float":
            w = QDoubleSpinBox()
            w.setRange(cfg.get("min", 0.0), cfg.get("max", 1_000_000.0))
            w.setDecimals(cfg.get("decimals", 2))
            w.setValue(float(cfg.get("value", 0.0)))
            w.setMinimumHeight(40)
            return w
        if ftype == "combo":
            w = QComboBox()
            for label, data in cfg.get("options", []):
                w.addItem(label, data)
            if "value" in cfg:
                idx = w.findData(cfg["value"])
                if idx >= 0:
                    w.setCurrentIndex(idx)
            w.setMinimumHeight(40)
            return w
        if ftype == "check":
            w = QCheckBox(cfg.get("text", ""))
            w.setChecked(bool(cfg.get("value", False)))
            return w
        raise ValueError(f"Unknown field type: {ftype}")

    def _value(self, key: str) -> Any:
        w = self._widgets[key]
        ftype = self._types[key]
        if ftype == "text":
            return w.text()
        if ftype == "int":
            return w.value()
        if ftype == "float":
            return w.value()
        if ftype == "combo":
            return w.currentData()
        if ftype == "check":
            return w.isChecked()
        return None

    def values(self) -> Dict[str, Any]:
        return {key: self._value(key) for key in self._widgets}

    def _submit(self) -> None:
        self._error.hide()
        try:
            self._on_submit(self.values())
        except AppError as exc:
            self._error.setText(str(exc))
            self._error.show()
            return
        self.accept()
