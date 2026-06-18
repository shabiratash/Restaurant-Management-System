"""Lightweight, fully responsive charts drawn with QPainter.

No third-party charting dependency — each chart repaints on resize so it
adapts to any window size while staying crisp.
"""
from __future__ import annotations

from typing import List, Tuple

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QLinearGradient
from PyQt5.QtWidgets import QSizePolicy, QWidget

from app.theme import Color, Font


class _BaseChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(180)
        self._font = QFont(Font.FAMILY, 8)

    def _empty(self, p: QPainter) -> None:
        p.setPen(QColor(Color.TEXT_SECONDARY))
        p.drawText(self.rect(), Qt.AlignCenter, "No data available")


class LineChart(_BaseChart):
    """Smooth area line chart for trends."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: List[Tuple[str, float]] = []

    def set_data(self, data: List[Tuple[str, float]]) -> None:
        self._data = data or []
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setFont(self._font)
        if not self._data:
            self._empty(p)
            return

        w, h = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 44, 16, 16, 28
        plot_w = max(1, w - pad_l - pad_r)
        plot_h = max(1, h - pad_t - pad_b)

        values = [v for _, v in self._data]
        vmax = max(values) or 1
        vmax *= 1.15
        n = len(self._data)
        step = plot_w / max(1, n - 1)

        # gridlines + y labels
        p.setPen(QPen(QColor(Color.BORDER), 1, Qt.DashLine))
        for i in range(5):
            y = pad_t + plot_h * i / 4
            p.drawLine(int(pad_l), int(y), int(w - pad_r), int(y))
            p.setPen(QColor(Color.TEXT_SECONDARY))
            val = vmax * (4 - i) / 4
            p.drawText(QRectF(0, y - 8, pad_l - 8, 16), Qt.AlignRight | Qt.AlignVCenter, f"{val:,.0f}")
            p.setPen(QPen(QColor(Color.BORDER), 1, Qt.DashLine))

        points = []
        for i, (_, v) in enumerate(self._data):
            x = pad_l + step * i
            y = pad_t + plot_h * (1 - v / vmax)
            points.append((x, y))

        # area gradient
        area = QPainterPath()
        area.moveTo(points[0][0], pad_t + plot_h)
        for x, y in points:
            area.lineTo(x, y)
        area.lineTo(points[-1][0], pad_t + plot_h)
        area.closeSubpath()
        grad = QLinearGradient(0, pad_t, 0, pad_t + plot_h)
        grad.setColorAt(0, QColor(37, 99, 235, 70))
        grad.setColorAt(1, QColor(37, 99, 235, 0))
        p.fillPath(area, grad)

        # line
        p.setPen(QPen(QColor(Color.PRIMARY), 2.4))
        path = QPainterPath()
        path.moveTo(*points[0])
        for x, y in points[1:]:
            path.lineTo(x, y)
        p.drawPath(path)

        # points + x labels
        for i, (x, y) in enumerate(points):
            p.setBrush(QColor(Color.SURFACE))
            p.setPen(QPen(QColor(Color.PRIMARY), 2))
            p.drawEllipse(QRectF(x - 3, y - 3, 6, 6))
            label = self._data[i][0][-5:]
            p.setPen(QColor(Color.TEXT_SECONDARY))
            p.drawText(QRectF(x - step / 2, h - pad_b + 6, step, 18), Qt.AlignCenter, label)
        p.end()


class BarChart(_BaseChart):
    """Vertical bar chart."""

    def __init__(self, parent=None, color: str = Color.PRIMARY):
        super().__init__(parent)
        self._data: List[Tuple[str, float]] = []
        self._color = color

    def set_data(self, data: List[Tuple[str, float]]) -> None:
        self._data = data or []
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setFont(self._font)
        if not self._data:
            self._empty(p)
            return
        w, h = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 40, 16, 16, 28
        plot_w = max(1, w - pad_l - pad_r)
        plot_h = max(1, h - pad_t - pad_b)
        vmax = (max(v for _, v in self._data) or 1) * 1.15
        n = len(self._data)
        slot = plot_w / n
        bar_w = slot * 0.55

        p.setPen(QPen(QColor(Color.BORDER), 1, Qt.DashLine))
        for i in range(5):
            y = pad_t + plot_h * i / 4
            p.drawLine(int(pad_l), int(y), int(w - pad_r), int(y))

        for i, (label, v) in enumerate(self._data):
            bh = plot_h * (v / vmax)
            x = pad_l + slot * i + (slot - bar_w) / 2
            y = pad_t + plot_h - bh
            grad = QLinearGradient(0, y, 0, y + bh)
            grad.setColorAt(0, QColor(self._color))
            grad.setColorAt(1, QColor(self._color).lighter(120))
            p.setBrush(grad)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(x, y, bar_w, bh), 5, 5)
            p.setPen(QColor(Color.TEXT_SECONDARY))
            p.drawText(QRectF(pad_l + slot * i, h - pad_b + 4, slot, 18), Qt.AlignCenter, label[:10])
        p.end()


class HBarChart(_BaseChart):
    """Horizontal bars — ideal for top-N rankings."""

    def __init__(self, parent=None, color: str = Color.SUCCESS):
        super().__init__(parent)
        self._data: List[Tuple[str, float]] = []
        self._color = color
        self.setMinimumHeight(160)

    def set_data(self, data: List[Tuple[str, float]]) -> None:
        self._data = data or []
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setFont(self._font)
        if not self._data:
            self._empty(p)
            return
        w, h = self.width(), self.height()
        pad = 12
        label_w = 110
        vmax = max(v for _, v in self._data) or 1
        n = len(self._data)
        row_h = (h - 2 * pad) / n
        bar_h = min(22, row_h * 0.55)

        for i, (label, v) in enumerate(self._data):
            cy = pad + row_h * i + row_h / 2
            p.setPen(QColor(Color.TEXT_PRIMARY))
            p.drawText(QRectF(0, cy - row_h / 2, label_w - 8, row_h), Qt.AlignRight | Qt.AlignVCenter, label[:16])
            track = QRectF(label_w, cy - bar_h / 2, w - label_w - pad - 36, bar_h)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(Color.BORDER))
            p.drawRoundedRect(track, bar_h / 2, bar_h / 2)
            fill_w = track.width() * (v / vmax)
            p.setBrush(QColor(self._color))
            p.drawRoundedRect(QRectF(track.x(), track.y(), fill_w, bar_h), bar_h / 2, bar_h / 2)
            p.setPen(QColor(Color.TEXT_SECONDARY))
            p.drawText(QRectF(track.right() + 4, cy - row_h / 2, 34, row_h),
                       Qt.AlignLeft | Qt.AlignVCenter, f"{v:,.0f}")
        p.end()
