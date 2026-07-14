"""Scrollable filmstrip timeline widget with playhead."""

from typing import List

import numpy as np
from PySide6.QtWidgets import QWidget, QScrollArea, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QImage, QPixmap, QMouseEvent


class _FilmstripBar(QWidget):
    position_changed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frames: List[np.ndarray] = []
        self._position = 0.0
        self._thumb_w = 80
        self._thumb_h = 45
        self._spacing = 2
        self._dragging = False
        self.setMouseTracking(True)
        self.setFixedHeight(self._thumb_h + 40)

    def set_frames(self, frames: List[np.ndarray]):
        self._frames = frames
        total_w = len(frames) * (self._thumb_w + self._spacing) + self._spacing
        self.setFixedWidth(max(total_w, self.parent().width() if self.parent() else total_w))
        self.update()

    def set_position(self, pos: float):
        self._position = max(0.0, min(pos, 1.0))
        self.update()

    def _frame_index(self, pos_x):
        total = max(len(self._frames), 1)
        idx = int(pos_x / max(self.width(), 1) * total)
        return max(0, min(idx, total - 1))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(26, 26, 26))

        if not self._frames:
            painter.setPen(QColor(80, 80, 80))
            painter.drawText(self.rect(), Qt.AlignCenter, "No frames")
            return

        x = self._spacing
        for i, arr in enumerate(self._frames):
            if arr.dtype != np.uint8:
                arr8 = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
            else:
                arr8 = arr
            hf, wf = arr8.shape[:2]
            qimg = QImage(arr8.data, wf, hf, wf * 3, QImage.Format_RGB888)
            pix = QPixmap.fromImage(qimg).scaled(
                self._thumb_w, self._thumb_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(x, 2, pix)
            painter.setPen(QPen(QColor(60, 60, 60), 1))
            painter.drawRect(x, 2, self._thumb_w, self._thumb_h)
            x += self._thumb_w + self._spacing

        ruler_y = self._thumb_h + 8
        ruler_h = 20
        total_frames = len(self._frames)
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.drawLine(0, ruler_y, self.width(), ruler_y)
        tick_interval = max(1, total_frames // 10)
        for i in range(0, total_frames, tick_interval):
            tx = self._spacing + i * (self._thumb_w + self._spacing) + self._thumb_w // 2
            painter.drawLine(tx, ruler_y, tx, ruler_y + 6)
            painter.setPen(QColor(120, 120, 120))
            secs = i / 24.0
            mins = int(secs // 60)
            secs_remain = int(secs % 60)
            painter.drawText(tx - 20, ruler_y + 8, 40, ruler_h - 8, Qt.AlignCenter,
                             f"{mins}:{secs_remain:02d}")
            painter.setPen(QPen(QColor(80, 80, 80), 1))

        ph_x = int(self._position * self.width())
        painter.setPen(QPen(QColor(220, 40, 40), 2))
        painter.drawLine(ph_x, 0, ph_x, self._thumb_h + ruler_h + 4)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._update_position(event.position().x())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            self._update_position(event.position().x())

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._dragging = False

    def _update_position(self, px):
        self._position = max(0.0, min(1.0, px / max(self.width(), 1)))
        self.update()
        self.position_changed.emit(self._position)


class TimelineWidget(QWidget):
    position_changed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setWidgetResizable(False)
        self._scroll.setStyleSheet("background-color: #1a1a1a; border: none;")

        self._bar = _FilmstripBar()
        self._bar.position_changed.connect(self._on_bar_position_changed)
        self._scroll.setWidget(self._bar)
        layout.addWidget(self._scroll)

    def set_frames(self, frames: List[np.ndarray]):
        self._bar.set_frames(frames)

    def set_position(self, pos: float):
        self._bar.set_position(pos)

    def _on_bar_position_changed(self, pos):
        self.position_changed.emit(pos)
