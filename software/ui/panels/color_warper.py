"""Grid-based color warper with interactive control points."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QMouseEvent


class ColorWarperPanel(QWidget):
    values_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid_size = 4
        self._grid = self._init_grid()
        self._drag = (-1, -1)
        self._build_ui()

    def _init_grid(self):
        n = self._grid_size
        return [[[j / (n - 1), i / (n - 1)] for j in range(n)] for i in range(n)]

    def _build_ui(self):
        self.setStyleSheet("background-color: #1a1a1a;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        title = QLabel("Color Warper")
        title.setStyleSheet("color: #888; font-size: 13px; font-weight: bold;")
        layout.addWidget(title)
        self._canvas = _WarperCanvas(self._grid, self._grid_size)
        self._canvas.values_changed.connect(self._on_canvas_change)
        layout.addWidget(self._canvas, 1)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        for text, cb in [("Reset", self._reset), ("4x4", lambda: self._set_n(4)),
                         ("6x6", lambda: self._set_n(6)), ("8x8", lambda: self._set_n(8))]:
            btn = QPushButton(text)
            btn.setStyleSheet(self._button_style())
            btn.clicked.connect(cb)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _set_n(self, n):
        self._grid_size = n
        self._grid = self._init_grid()
        self._canvas.set_grid(self._grid, n)
        self._emit()

    def _on_canvas_change(self, grid):
        self._grid = grid
        self._emit()

    def _emit(self):
        self.values_changed.emit(self._grid)

    def _reset(self):
        self._grid = self._init_grid()
        self._canvas.set_grid(self._grid, self._grid_size)
        self._emit()

    @staticmethod
    def _button_style():
        return "QPushButton { background-color: #333; color: #888; border: 1px solid #444; border-radius: 4px; padding: 6px 16px; font-size: 12px; } QPushButton:hover { background-color: #444; color: #aaa; }"


class _WarperCanvas(QWidget):
    values_changed = Signal(object)

    def __init__(self, grid, n, parent=None):
        super().__init__(parent)
        self._grid = grid
        self._n = n
        self._drag = (-1, -1)
        self.setMinimumSize(200, 200)
        self.setStyleSheet("background-color: #222; border: 1px solid #333; border-radius: 4px;")

    def set_grid(self, grid, n):
        self._grid = grid
        self._n = n
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(34, 34, 34))
        w, h = self.width(), self.height()
        margin = 20
        gw = w - 2 * margin
        gh = h - 2 * margin
        n = self._n
        p.setPen(QPen(QColor(60, 60, 70), 1))
        for i in range(n):
            for j in range(n):
                x = margin + self._grid[i][j][0] * gw
                y = margin + self._grid[i][j][1] * gh
                if i < n - 1:
                    nx = margin + self._grid[i + 1][j][0] * gw
                    ny = margin + self._grid[i + 1][j][1] * gh
                    p.drawLine(x, y, nx, ny)
                if j < n - 1:
                    nx = margin + self._grid[i][j + 1][0] * gw
                    ny = margin + self._grid[i][j + 1][1] * gh
                    p.drawLine(x, y, nx, ny)
        p.setBrush(QColor(100, 180, 255))
        p.setPen(QPen(QColor(200, 200, 200), 1))
        for i in range(n):
            for j in range(n):
                x = margin + self._grid[i][j][0] * gw
                y = margin + self._grid[i][j][1] * gh
                p.drawEllipse(x - 3, y - 3, 6, 6)

    def mousePressEvent(self, event):
        self._drag = self._hit(event.position())
        if self._drag[0] >= 0:
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self._drag[0] >= 0:
            i, j = self._drag
            margin = 20
            gw = self.width() - 2 * margin
            gh = self.height() - 2 * margin
            self._grid[i][j] = [
                max(0, min(1, (event.position().x() - margin) / max(gw, 1))),
                max(0, min(1, (event.position().y() - margin) / max(gh, 1))),
            ]
            self.update()
            self.values_changed.emit(self._grid)

    def mouseReleaseEvent(self, event):
        self._drag = (-1, -1)
        self.setCursor(Qt.ArrowCursor)

    def mouseDoubleClickEvent(self, event):
        self._grid = [[j / (self._n - 1) for j in range(self._n)] for i in range(self._n)]
        self.update()
        self.values_changed.emit(self._grid)

    def _hit(self, pos):
        margin = 20
        gw = self.width() - 2 * margin
        gh = self.height() - 2 * margin
        for i in range(self._n):
            for j in range(self._n):
                x = margin + self._grid[i][j][0] * gw
                y = margin + self._grid[i][j][1] * gh
                if abs(pos.x() - x) < 10 and abs(pos.y() - y) < 10:
                    return (i, j)
        return (-1, -1)
