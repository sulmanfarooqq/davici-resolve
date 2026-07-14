"""Gradient bar widget with draggable color stop handles."""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient, QMouseEvent


class ColorSlider(QWidget):
    handles_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._channel = 'red'
        self._stops = [(0.0, 0.0), (1.0, 1.0)]
        self._drag_idx = -1
        self.setMinimumSize(200, 30)
        self.setFixedHeight(30)

    def set_stops(self, stops):
        self._stops = sorted(stops, key=lambda s: s[0])
        self.update()

    def get_stops(self):
        return list(self._stops)

    def set_channel(self, channel):
        if channel in ('red', 'green', 'blue', 'luma', 'alpha'):
            self._channel = channel
            self.update()

    def _channel_color(self, t):
        if self._channel == 'red':
            return QColor(int(t * 255), 0, 0)
        elif self._channel == 'green':
            return QColor(0, int(t * 255), 0)
        elif self._channel == 'blue':
            return QColor(0, 0, int(t * 255))
        elif self._channel == 'luma':
            v = int(t * 255)
            return QColor(v, v, v)
        elif self._channel == 'alpha':
            return QColor(80, 80, 80, int(t * 255))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect().adjusted(4, 4, -4, -4)

        grad = QLinearGradient(r.topLeft(), r.topRight())
        if self._stops:
            for pos, val in self._stops:
                grad.setColorAt(pos, self._channel_color(val))
        else:
            grad.setColorAt(0.0, QColor(30, 30, 30))
            grad.setColorAt(1.0, QColor(30, 30, 30))

        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawRect(r)

        for pos, val in self._stops:
            x = r.left() + pos * r.width()
            painter.setPen(QPen(QColor(180, 180, 180), 1))
            painter.setBrush(QColor(200, 200, 200))
            painter.drawRect(int(x) - 3, r.top() - 2, 6, r.height() + 4)

    def _pos_to_val(self, px):
        r = self.rect().adjusted(4, 4, -4, -4)
        return max(0.0, min(1.0, (px - r.left()) / max(r.width(), 1)))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            v = self._pos_to_val(event.position().x())
            for i, (pos, val) in enumerate(self._stops):
                if abs(v - pos) < 0.04:
                    self._drag_idx = i
                    return
            closest = min(range(len(self._stops)), key=lambda i: abs(self._stops[i][0] - v))
            pos, val = self._stops[closest]
            if abs(v - pos) < 0.08:
                self._drag_idx = closest
            else:
                self._stops.append((v, val))
                self._stops.sort(key=lambda s: s[0])
                self._drag_idx = self._stops.index((v, val))
                self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_idx >= 0:
            v = self._pos_to_val(event.position().x())
            pos, val = self._stops[self._drag_idx]
            self._stops[self._drag_idx] = (v, val)
            self._stops.sort(key=lambda s: s[0])
            self._drag_idx = self._stops.index((v, val))
            self.update()
            self.handles_changed.emit(list(self._stops))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._drag_idx >= 0:
            if len(self._stops) > 2:
                pos, val = self._stops[self._drag_idx]
                if pos <= 0.01 or pos >= 0.99:
                    self._stops.pop(self._drag_idx)
                    self._stops.sort(key=lambda s: s[0])
                    self.update()
                    self.handles_changed.emit(list(self._stops))
        self._drag_idx = -1
