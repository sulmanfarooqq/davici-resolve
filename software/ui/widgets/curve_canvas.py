"""Interactive curve editor widget with multi-channel support and signal emission."""
import numpy as np
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QMouseEvent


CHANNEL_COLORS = {
    'RGB': QColor(200, 200, 200),
    'R': QColor(220, 80, 80),
    'G': QColor(80, 200, 80),
    'B': QColor(80, 120, 220),
    'H': QColor(200, 200, 80),
    'S': QColor(200, 80, 200),
    'L': QColor(180, 180, 180),
}


class CurveCanvas(QWidget):
    curveChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self._channels = {
            'RGB': [(0.0, 0.0), (1.0, 1.0)],
            'R': [(0.0, 0.0), (1.0, 1.0)],
            'G': [(0.0, 0.0), (1.0, 1.0)],
            'B': [(0.0, 0.0), (1.0, 1.0)],
        }
        self._active_channel = 'RGB'
        self.points = self._channels['RGB']
        self.drag_idx = -1
        self.bg_color = QColor(40, 40, 40)
        self.grid_color = QColor(60, 60, 60)
        self.setMouseTracking(True)

    def set_active_channel(self, ch: str):
        if ch in self._channels:
            self._active_channel = ch
            self.points = self._channels[ch]
            self.update()

    def get_all_curves(self):
        return dict(self._channels)

    def set_all_curves(self, curves: dict):
        for ch, pts in curves.items():
            if ch in self._channels:
                self._channels[ch] = list(pts)
        self.points = self._channels.get(self._active_channel, self._channels['RGB'])
        self.update()

    def _to_widget(self, x, y):
        m = min(self.width(), self.height()) - 20
        return QPointF(10 + x * m, 10 + (1 - y) * m)

    def _to_data(self, px, py):
        m = min(self.width(), self.height()) - 20
        x = (px - 10) / m
        y = 1 - (py - 10) / m
        return x, y

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), self.bg_color)
        m = min(self.width(), self.height()) - 20
        p.setPen(QPen(self.grid_color, 1))
        for i in range(11):
            x = 10 + i * m / 10
            p.drawLine(QPointF(x, 10), QPointF(x, 10 + m))
            y = 10 + i * m / 10
            p.drawLine(QPointF(10, y), QPointF(10 + m, y))
        p.setPen(QPen(QColor(80, 80, 80), 1, Qt.DashLine))
        p.drawLine(self._to_widget(0, 0), self._to_widget(1, 1))
        from core.curves_nodes import evaluate_curve
        xs = [i / 100 for i in range(101)]
        pts = self._channels.get(self._active_channel, [(0, 0), (1, 1)])
        ys = evaluate_curve(pts, np.array(xs, dtype=np.float32))
        curve_color = CHANNEL_COLORS.get(self._active_channel, QColor(200, 200, 200))
        p.setPen(QPen(curve_color, 2))
        for i in range(100):
            p1 = self._to_widget(xs[i], ys[i])
            p2 = self._to_widget(xs[i + 1], ys[i + 1])
            p.drawLine(p1, p2)
        for pt in pts:
            wp = self._to_widget(*pt)
            p.setBrush(QBrush(curve_color))
            p.setPen(QPen(QColor(255, 255, 255), 1))
            p.drawEllipse(wp, 5, 5)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            px, py = event.position().x(), event.position().y()
            for i, pt in enumerate(self.points):
                wp = self._to_widget(*pt)
                if abs(px - wp.x()) < 8 and abs(py - wp.y()) < 8:
                    self.drag_idx = i
                    return
            x, y = self._to_data(px, py)
            self.points.append((max(0, min(1, x)), max(0, min(1, y))))
            self.points.sort(key=lambda p: p[0])
            self._channels[self._active_channel] = list(self.points)
            self.update()
            self.curveChanged.emit()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drag_idx >= 0:
            x, y = self._to_data(event.position().x(), event.position().y())
            x = max(0, min(1, x))
            y = max(0, min(1, y))
            if 0 < self.drag_idx < len(self.points) - 1:
                self.points[self.drag_idx] = (x, y)
                self.points.sort(key=lambda p: p[0])
                self.drag_idx = next(i for i, p in enumerate(self.points) if p == (x, y))
            self._channels[self._active_channel] = list(self.points)
            self.update()
            self.curveChanged.emit()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.drag_idx = -1

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        px, py = event.position().x(), event.position().y()
        for i, pt in enumerate(self.points):
            if i in (0, len(self.points) - 1):
                continue
            wp = self._to_widget(*pt)
            if abs(px - wp.x()) < 8 and abs(py - wp.y()) < 8:
                self.points.pop(i)
                self._channels[self._active_channel] = list(self.points)
                self.update()
                self.curveChanged.emit()
                return

    def reset_current(self):
        self.points = [(0.0, 0.0), (1.0, 1.0)]
        self._channels[self._active_channel] = list(self.points)
        self.update()
        self.curveChanged.emit()

    def reset_all(self):
        for ch in self._channels:
            self._channels[ch] = [(0.0, 0.0), (1.0, 1.0)]
        self.points = self._channels[self._active_channel]
        self.update()
        self.curveChanged.emit()

    def set_points(self, pts):
        self.points = pts
        self._channels[self._active_channel] = list(pts)
        self.update()

    def get_points(self):
        return self.points
