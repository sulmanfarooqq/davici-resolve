"""Gradient slider widget for qualifier ranges."""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient, QMouseEvent


class GradientSlider(QWidget):
    range_changed = Signal(float, float)

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(parent)
        self._min = 0.0
        self._max = 1.0
        self._low = 0.2
        self._high = 0.8
        self._soft_low = 0.1
        self._soft_high = 0.9
        self._drag_target = None
        self.setMinimumSize(100, 24)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect().adjusted(2, 4, -2, -4)
        # Background gradient
        grad = QLinearGradient(r.topLeft(), r.topRight())
        grad.setColorAt(0, QColor(30, 30, 30))
        grad.setColorAt(1, QColor(30, 30, 30))
        p.fillRect(r, QBrush(grad))
        # Soft range
        sr = QRectF(
            r.left() + self._soft_low * r.width(), r.top(),
            (self._soft_high - self._soft_low) * r.width(), r.height()
        )
        p.fillRect(sr, QColor(60, 60, 60))
        # Hard range
        hr = QRectF(
            r.left() + self._low * r.width(), r.top(),
            (self._high - self._low) * r.width(), r.height()
        )
        grad2 = QLinearGradient(hr.topLeft(), hr.topRight())
        grad2.setColorAt(0, QColor(80, 120, 180))
        grad2.setColorAt(1, QColor(80, 120, 180))
        p.fillRect(hr, QBrush(grad2))
        # Border
        p.setPen(QPen(QColor(100, 100, 100), 1))
        p.drawRect(r)
        # Handles
        for pos, color in [(self._low, QColor(200, 200, 200)),
                           (self._high, QColor(200, 200, 200)),
                           (self._soft_low, QColor(100, 100, 100)),
                           (self._soft_high, QColor(100, 100, 100))]:
            x = r.left() + pos * r.width()
            p.setPen(QPen(color, 2))
            p.drawLine(int(x), r.top(), int(x), r.bottom())

    def _pos_to_val(self, px):
        r = self.rect().adjusted(2, 4, -2, -4)
        return max(0.0, min(1.0, (px - r.left()) / max(r.width(), 1)))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            v = self._pos_to_val(event.position().x())
            for name, attr in [('soft_low', '_soft_low'), ('low', '_low'),
                               ('high', '_high'), ('soft_high', '_soft_high')]:
                if abs(v - getattr(self, attr)) < 0.03:
                    self._drag_target = attr
                    return
            # Center
            self._drag_target = '_low'

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_target:
            v = self._pos_to_val(event.position().x())
            setattr(self, self._drag_target, v)
            # Enforce ordering
            self._soft_low = min(self._soft_low, self._low)
            self._low = max(self._low, self._soft_low)
            self._high = max(self._high, self._low)
            self._soft_high = max(self._soft_high, self._high)
            self.update()
            self.range_changed.emit(self._low, self._high)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_target = None

    def set_range(self, low, high, soft_low=0.0, soft_high=1.0):
        self._low = low
        self._high = high
        self._soft_low = soft_low
        self._soft_high = soft_high
        self.update()

    def get_range(self):
        return self._low, self._high, self._soft_low, self._soft_high
