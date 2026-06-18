"""Vector line-icons drawn with QPainter.

Avoids shipping image assets or relying on emoji glyphs. Each icon is drawn
into a QPixmap at the requested size and color, giving crisp, recolorable
icons that match the design system.
"""
from __future__ import annotations

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap


def _pen(painter: QPainter, color: str, width: float) -> None:
    pen = QPen(QColor(color))
    pen.setWidthF(width)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)


def make_icon(name: str, color: str = "#64748B", size: int = 22) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    _pen(p, color, max(1.6, size * 0.085))
    s = size
    m = s * 0.18  # margin

    if name == "dashboard":
        p.drawRoundedRect(QRectF(m, m, s * 0.28, s * 0.28), 2, 2)
        p.drawRoundedRect(QRectF(s * 0.54, m, s * 0.28, s * 0.28), 2, 2)
        p.drawRoundedRect(QRectF(m, s * 0.54, s * 0.28, s * 0.28), 2, 2)
        p.drawRoundedRect(QRectF(s * 0.54, s * 0.54, s * 0.28, s * 0.28), 2, 2)
    elif name == "orders":
        p.drawRoundedRect(QRectF(s * 0.24, m, s * 0.52, s * 0.66), 3, 3)
        p.drawLine(int(s * 0.36), int(s * 0.4), int(s * 0.64), int(s * 0.4))
        p.drawLine(int(s * 0.36), int(s * 0.55), int(s * 0.64), int(s * 0.55))
        p.drawLine(int(s * 0.36), int(s * 0.18), int(s * 0.36), int(s * 0.26))
        p.drawLine(int(s * 0.64), int(s * 0.18), int(s * 0.64), int(s * 0.26))
    elif name == "menu":
        # fork & knife
        cx = s * 0.4
        p.drawLine(int(cx), int(m), int(cx), int(s - m))
        p.drawLine(int(cx - s * 0.12), int(m), int(cx - s * 0.12), int(s * 0.4))
        p.drawLine(int(cx + s * 0.12), int(m), int(cx + s * 0.12), int(s * 0.4))
        p.drawLine(int(cx - s * 0.12), int(s * 0.4), int(cx + s * 0.12), int(s * 0.4))
        p.drawLine(int(s * 0.72), int(m), int(s * 0.72), int(s - m))
        p.drawArc(QRectF(s * 0.6, m, s * 0.24, s * 0.4), 0, 180 * 16)
    elif name == "customers":
        p.drawEllipse(QRectF(s * 0.34, m, s * 0.32, s * 0.32))
        path = QPainterPath()
        path.moveTo(s * 0.22, s - m)
        path.arcTo(QRectF(s * 0.22, s * 0.52, s * 0.56, s * 0.56), 180, -180)
        p.drawPath(path)
    elif name == "inventory":
        p.drawRect(QRectF(m, s * 0.32, s - 2 * m, s * 0.5))
        p.drawLine(int(m), int(s * 0.32), int(s / 2), int(m))
        p.drawLine(int(s - m), int(s * 0.32), int(s / 2), int(m))
        p.drawLine(int(s / 2), int(m), int(s / 2), int(s * 0.82))
    elif name == "reports":
        p.drawLine(int(m), int(s - m), int(m), int(m))
        p.drawLine(int(m), int(s - m), int(s - m), int(s - m))
        p.drawLine(int(s * 0.34), int(s * 0.7), int(s * 0.34), int(s * 0.55))
        p.drawLine(int(s * 0.52), int(s * 0.7), int(s * 0.52), int(s * 0.4))
        p.drawLine(int(s * 0.7), int(s * 0.7), int(s * 0.7), int(s * 0.3))
    elif name == "settings":
        p.drawEllipse(QRectF(s * 0.36, s * 0.36, s * 0.28, s * 0.28))
        for ang in range(0, 360, 45):
            import math
            a = math.radians(ang)
            cx, cy = s / 2, s / 2
            r1, r2 = s * 0.34, s * 0.46
            p.drawLine(int(cx + r1 * math.cos(a)), int(cy + r1 * math.sin(a)),
                       int(cx + r2 * math.cos(a)), int(cy + r2 * math.sin(a)))
    elif name == "logout":
        p.drawLine(int(s * 0.45), int(m), int(s * 0.45), int(s - m))
        p.drawArc(QRectF(m, m, s * 0.7, s - 2 * m), 60 * 16, 240 * 16)
    elif name == "revenue":
        p.drawEllipse(QRectF(m, m, s - 2 * m, s - 2 * m))
        p.drawLine(int(s / 2), int(s * 0.3), int(s / 2), int(s * 0.7))
        p.drawText(QRectF(0, 0, s, s), Qt.AlignCenter, "$")
    elif name == "table":
        p.drawEllipse(QRectF(m, s * 0.28, s - 2 * m, s * 0.3))
        p.drawLine(int(s * 0.3), int(s * 0.5), int(s * 0.3), int(s - m))
        p.drawLine(int(s * 0.7), int(s * 0.5), int(s * 0.7), int(s - m))
    elif name == "search":
        p.drawEllipse(QRectF(m, m, s * 0.5, s * 0.5))
        p.drawLine(int(s * 0.6), int(s * 0.6), int(s - m), int(s - m))
    elif name == "plus":
        p.drawLine(int(s / 2), int(m), int(s / 2), int(s - m))
        p.drawLine(int(m), int(s / 2), int(s - m), int(s / 2))
    elif name == "clock":
        p.drawEllipse(QRectF(m, m, s - 2 * m, s - 2 * m))
        p.drawLine(int(s / 2), int(s / 2), int(s / 2), int(s * 0.3))
        p.drawLine(int(s / 2), int(s / 2), int(s * 0.66), int(s / 2))
    p.end()
    return pm
