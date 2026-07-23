"""Waveform / vectorscope / histogram scope widget using QPainter."""

import numpy as np
try:
    from PySide6.QtWidgets import QOpenGLWidget
    _ScopeBase = QOpenGLWidget
except ImportError:
    from PySide6.QtWidgets import QWidget
    _ScopeBase = QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QFont


class ScopeGL(_ScopeBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode = 'waveform'
        self._image = None
        self.setMinimumSize(320, 180)
        self._bg = QColor(26, 26, 26)
        self._trace = QColor(68, 170, 68)

    def set_mode(self, mode):
        if mode in ('waveform', 'histogram', 'vectorscope'):
            self._mode = mode
            self.update()

    def set_image(self, arr: np.ndarray):
        self._image = arr
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), self._bg)

        if self._image is None:
            painter.setPen(QColor(80, 80, 80))
            painter.drawText(self.rect(), Qt.AlignCenter, "No Signal")
            painter.end()
            return

        if self._mode == 'waveform':
            self._draw_waveform(painter)
        elif self._mode == 'histogram':
            self._draw_histogram(painter)
        elif self._mode == 'vectorscope':
            self._draw_vectorscope(painter)

        painter.end()

    def _draw_waveform(self, painter):
        h = self.height()
        w = self.width()
        arr = self._image
        if arr.dtype != np.uint8:
            arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
        luma = 0.2126 * arr[:,:,0].astype(np.float32) + 0.7152 * arr[:,:,1].astype(np.float32) + 0.0722 * arr[:,:,2].astype(np.float32)
        luma = luma / 255.0

        pen = QPen(self._trace, 1)
        painter.setPen(pen)
        step = max(1, luma.shape[0] // h)
        for row_y in range(0, luma.shape[0], step):
            row = luma[row_y, :]
            for x in range(0, w):
                col_idx = int(x * len(row) / w)
                l_val = row[col_idx]
                py = int((h - 1) - l_val * (h - 1))
                painter.drawPoint(x, py)

        painter.setPen(QPen(QColor(42, 42, 42), 1))
        for i in range(5):
            gy = int(i * h / 4)
            painter.drawLine(0, gy, w, gy)

    def _draw_histogram(self, painter):
        h = self.height()
        w = self.width()
        arr = self._image
        if arr.dtype != np.uint8:
            arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)

        colors = [
            QColor(255, 68, 68),
            QColor(68, 255, 68),
            QColor(68, 68, 255),
        ]
        bin_count = 256
        bar_w = max(1, w // bin_count)
        for ch in range(3):
            data = arr[:,:,ch].ravel()
            hist = np.bincount(data.astype(np.int32), minlength=256)
            hist = np.log1p(hist.astype(np.float32))
            mx = hist.max()
            if mx > 0:
                hist = hist / mx
            painter.setPen(Qt.NoPen)
            painter.setBrush(colors[ch])
            for i in range(bin_count):
                bh = int(hist[i] * (h - 4))
                if bh > 0:
                    x = int(i * w / bin_count)
                    painter.drawRect(x, h - 4 - bh, bar_w, bh)

    def _draw_vectorscope(self, painter):
        h = self.height()
        w = self.width()
        cx = w // 2
        cy = h // 2
        radius = min(cx, cy) - 8

        arr = self._image
        if arr.dtype != np.uint8:
            arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
        rgb = arr[:,:,:3].astype(np.float32) / 255.0

        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        cb = 0.5389 * (b - y)
        cr = 0.6350 * (r - y)

        painter.setPen(QPen(QColor(60, 180, 60, 100), 1))
        step = max(1, cb.shape[0] * cb.shape[1] // 20000)
        flat_cb = cb.ravel()[::step]
        flat_cr = cr.ravel()[::step]
        for i in range(len(flat_cb)):
            px = int(cx + flat_cb[i] * radius)
            py = int(cy + flat_cr[i] * radius)
            if 0 <= px < w and 0 <= py < h:
                painter.drawPoint(px, py)

        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)
        painter.drawLine(cx - radius, cy, cx + radius, cy)
        painter.drawLine(cx, cy - radius, cx, cy + radius)

        color_bar_targets = [
            (1.0, 0.0, 0.0, 0.0, 0.5),   # R
            (0.0, 1.0, 0.0, 0.5, 0.0),   # G
            (0.0, 0.0, 1.0, 0.5, 0.5),   # B
            (1.0, 1.0, 0.0, 0.5, 0.0),   # Y
            (0.0, 1.0, 1.0, 0.0, 0.5),   # C
            (1.0, 0.0, 1.0, 0.5, 0.5),   # M
        ]
        for rr, gg, bb, *_ in color_bar_targets:
            yy = 0.2126 * rr + 0.7152 * gg + 0.0722 * bb
            ccb = 0.5389 * (bb - yy)
            ccr = 0.6350 * (rr - yy)
            tx = int(cx + ccb * radius * 0.75)
            ty = int(cy + ccr * radius * 0.75)
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(tx - 4, ty - 4, 8, 8)
