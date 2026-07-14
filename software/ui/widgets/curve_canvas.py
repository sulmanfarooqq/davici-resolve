"""Interactive curve editor widget."""
import numpy as np
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QMouseEvent


class CurveCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.points = [(0.0, 0.0), (1.0, 1.0)]
        self.drag_idx = -1
        self.bg_color = QColor(40, 40, 40)
        self.grid_color = QColor(60, 60, 60)
        self.curve_color = QColor(200, 200, 200)
        self.point_color = QColor(100, 180, 255)
        self.setMouseTracking(True)

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
        # Grid
        p.setPen(QPen(self.grid_color, 1))
        for i in range(11):
            x = 10 + i * m / 10
            p.drawLine(QPointF(x, 10), QPointF(x, 10 + m))
            y = 10 + i * m / 10
            p.drawLine(QPointF(10, y), QPointF(10 + m, y))
        # Curve (evaluate via LUT from core)
        from core.curves_nodes import evaluate_curve
        xs = [i / 100 for i in range(101)]
        ys = evaluate_curve(self.points, np.array(xs, dtype=np.float32))
        p.setPen(QPen(self.curve_color, 2))
        for i in range(100):
            p1 = self._to_widget(xs[i], ys[i])
            p2 = self._to_widget(xs[i+1], ys[i+1])
            p.drawLine(p1, p2)
        # Points
        for pt in self.points:
            wp = self._to_widget(*pt)
            p.setBrush(QBrush(self.point_color))
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
            # Add point
            x, y = self._to_data(px, py)
            self.points.append((max(0, min(1, x)), max(0, min(1, y))))
            self.points.sort(key=lambda p: p[0])
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drag_idx >= 0:
            x, y = self._to_data(event.position().x(), event.position().y())
            x = max(0, min(1, x))
            y = max(0, min(1, y))
            if self.drag_idx > 0 and self.drag_idx < len(self.points) - 1:
                self.points[self.drag_idx] = (x, y)
                self.points.sort(key=lambda p: p[0])
                self.drag_idx = self.points.index((x, y))
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.drag_idx = -1
        if len(self.points) > 2:
            self.points = [self.points[0]] + sorted(self.points[1:-1], key=lambda p: p[0]) + [self.points[-1]]
        self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        px, py = event.position().x(), event.position().y()
        for i, pt in enumerate(self.points):
            if i in (0, len(self.points) - 1):
                continue
            wp = self._to_widget(*pt)
            if abs(px - wp.x()) < 8 and abs(py - wp.y()) < 8:
                self.points.pop(i)
                self.update()
                return

    def set_points(self, pts):
        self.points = pts
        self.update()

    def get_points(self):
        return self.points
