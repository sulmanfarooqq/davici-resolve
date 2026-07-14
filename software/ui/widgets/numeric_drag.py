"""Click-drag numeric input widget (DaVinci Resolve style)."""
from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QKeyEvent


class NumericDrag(QLineEdit):
    value_changed = Signal(float)

    def __init__(self, value=0.0, min_val=-10.0, max_val=10.0, step=0.01, parent=None):
        super().__init__(parent)
        self._val = value
        self._min = min_val
        self._max = max_val
        self._step = step
        self._drag_start = None
        self._drag_start_val = value
        self.setAlignment(Qt.AlignCenter)
        self.setFixedWidth(60)
        self.setText(f"{value:.3f}")
        self.setStyleSheet("""
            QLineEdit {
                background: #2a2a2a; color: #ccc; border: 1px solid #444;
                border-radius: 3px; padding: 2px 4px; font-size: 11px;
            }
            QLineEdit:hover { border-color: #666; }
            QLineEdit:focus { border-color: #888; }
        """)
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text):
        try:
            v = float(text)
            self._val = max(self._min, min(self._max, v))
            self.value_changed.emit(self._val)
        except ValueError:
            pass

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.position().x()
            self._drag_start_val = self._val
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_start is not None:
            dx = event.position().x() - self._drag_start
            if abs(dx) > 2:
                self._val = max(self._min, min(self._max,
                    self._drag_start_val + dx * self._step))
                self.setText(f"{self._val:.3f}")
                self.value_changed.emit(self._val)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_start = None
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Up:
            self._val = max(self._min, min(self._max, self._val + self._step))
            self.setText(f"{self._val:.3f}")
            self.value_changed.emit(self._val)
        elif event.key() == Qt.Key_Down:
            self._val = max(self._min, min(self._max, self._val - self._step))
            self.setText(f"{self._val:.3f}")
            self.value_changed.emit(self._val)
        else:
            super().keyPressEvent(event)

    def set_value(self, v):
        self._val = max(self._min, min(self._max, v))
        self.setText(f"{self._val:.3f}")

    def value(self):
        return self._val
