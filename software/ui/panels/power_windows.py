"""Power Windows panel: shape mask creation and compositing."""

import numpy as np
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QListWidget, QPushButton,
                               QVBoxLayout, QWidget)
from PySide6.QtGui import QPainter, QPen, QColor, QMouseEvent, QBrush
from core.color_math import get_luminance


class PowerWindowsPanel(QWidget):
    mask_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_shape = None
        self._masks = []
        self._drawing = False
        self._start_pt = None
        self._current_pt = None
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: #1a1a1a;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        title = QLabel("Power Windows")
        title.setStyleSheet("color: #888; font-size: 13px; font-weight: bold;")
        layout.addWidget(title)
        self._indicator = QLabel("Active Mask: None")
        self._indicator.setStyleSheet("color: #666; font-size: 11px; padding: 4px 0;")
        layout.addWidget(self._indicator)
        for shape in ["Circle", "Rectangle", "Gradient"]:
            btn = QPushButton(shape)
            btn.setStyleSheet(self._shape_button_style())
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, s=shape: self._select_shape(s))
            layout.addWidget(btn)
        self._mask_list = QListWidget()
        self._mask_list.setStyleSheet(self._list_style())
        self._mask_list.setMinimumHeight(80)
        layout.addWidget(self._mask_list, 1)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        for text, cb in [("Add Mask", self._on_add_mask), ("Remove Mask", self._on_remove_mask)]:
            btn = QPushButton(text)
            btn.setStyleSheet(self._action_button_style())
            btn.clicked.connect(cb)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

    def _select_shape(self, shape):
        self._active_shape = shape
        self._indicator.setText(f"Active Mask: {shape}")

    def _on_add_mask(self):
        if self._active_shape:
            self._mask_list.addItem(self._active_shape)
            self._masks.append({'type': self._active_shape, 'params': {}})
            self.mask_changed.emit(self._masks)

    def _on_remove_mask(self):
        row = self._mask_list.currentRow()
        if row >= 0:
            self._mask_list.takeItem(row)
            self._masks.pop(row)
            self.mask_changed.emit(self._masks)

    def render_mask(self, width, height):
        mask = np.zeros((height, width), dtype=np.float32)
        for m in self._masks:
            p = m['params']
            if m['type'] == 'Circle':
                cx, cy = p.get('cx', width // 2), p.get('cy', height // 2)
                r = p.get('r', min(width, height) // 4)
                yy, xx = np.ogrid[:height, :width]
                dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
                mask = np.maximum(mask, 1.0 - np.clip(dist / r, 0, 1))
            elif m['type'] == 'Rectangle':
                x0, y0 = p.get('x0', width // 4), p.get('y0', height // 4)
                x1, y1 = p.get('x1', 3 * width // 4), p.get('y1', 3 * height // 4)
                yy, xx = np.ogrid[:height, :width]
                mask = np.maximum(mask, ((xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)).astype(np.float32))
        return mask

    def set_shape_params(self, shape_type, params):
        for m in self._masks:
            if m['type'] == shape_type:
                m['params'].update(params)
                break
        self.mask_changed.emit(self._masks)

    @staticmethod
    def _shape_button_style():
        return """QPushButton { background-color: #2a2a2a; color: #888; border: 1px solid #3a3a3a; border-radius: 4px; padding: 8px 12px; font-size: 12px; text-align: left; }
QPushButton:hover { background-color: #333; color: #aaa; border-color: #555; }
QPushButton:pressed { background-color: #3a3a3a; }"""

    @staticmethod
    def _action_button_style():
        return """QPushButton { background-color: #333; color: #888; border: 1px solid #444; border-radius: 4px; padding: 6px 16px; font-size: 12px; }
QPushButton:hover { background-color: #444; color: #aaa; }"""

    @staticmethod
    def _list_style():
        return """QListWidget { background-color: #222; border: 1px solid #333; border-radius: 4px; color: #888; font-size: 12px; outline: none; }
QListWidget::item:selected { background-color: #3a3a3a; color: #aaa; }"""
