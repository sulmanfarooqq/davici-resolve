"""Gallery panel: save/load stills as PNG + grade JSON sidecar."""

import json, os
import numpy as np
from PIL import Image
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
                               QPushButton, QSizePolicy, QVBoxLayout, QWidget,
                               QFileDialog, QMessageBox)
from core.project import GradeParams


class GalleryPanel(QWidget):
    still_loaded = Signal(object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stills = []
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: #1a1a1a;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        title = QLabel("Gallery")
        title.setStyleSheet("color: #888; font-size: 13px; font-weight: bold;")
        layout.addWidget(title)
        self._stills_list = QListWidget()
        self._stills_list.setStyleSheet(self._list_style())
        self._stills_list.setIconSize(QSize(60, 40))
        self._stills_list.setMinimumHeight(160)
        self._stills_list.itemDoubleClicked.connect(self._on_load)
        list_size = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._stills_list.setSizePolicy(list_size)
        layout.addWidget(self._stills_list)
        preview_area = QWidget()
        preview_area.setFixedHeight(80)
        preview_area.setStyleSheet("background-color: #222; border: 1px solid #333; border-radius: 4px;")
        preview_layout = QVBoxLayout(preview_area)
        preview_layout.setAlignment(Qt.AlignCenter)
        self._preview_label = QLabel("Double-click to load")
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setStyleSheet("color: #555; font-size: 11px; border: none;")
        preview_layout.addWidget(self._preview_label)
        layout.addWidget(preview_area)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        for text, cb in [("Save Still", self._on_save), ("Load Still", self._on_load),
                         ("Delete", self._on_delete)]:
            btn = QPushButton(text)
            btn.setStyleSheet(self._button_style())
            btn.clicked.connect(cb)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)
        self._memory_label = QLabel("Memory: 0 stills")
        self._memory_label.setStyleSheet("color: #666; font-size: 11px; padding: 2px 0;")
        layout.addWidget(self._memory_label)
        layout.addStretch()

    def add_still(self, name: str, frame: np.ndarray, grade: dict):
        self._stills.append({'name': name, 'frame': frame.copy(), 'grade': grade.copy()})
        item = QListWidgetItem(name)
        self._stills_list.addItem(item)
        self._update_memory()

    def _on_save(self):
        if not self._stills:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Still", "", "PNG (*.png)")
        if not path:
            return
        still = self._stills[-1]
        arr = np.clip(still['frame'] * 255.0, 0, 255).astype(np.uint8)
        Image.fromarray(arr).save(path)
        grade_path = os.path.splitext(path)[0] + ".json"
        with open(grade_path, "w") as f:
            json.dump(still['grade'], f, indent=2)

    def _on_load(self):
        row = self._stills_list.currentRow()
        if row >= 0:
            still = self._stills[row]
            self.still_loaded.emit(still['frame'], still['grade'])
            self._preview_label.setText(f"Loaded: {still['name']}")

    def _on_delete(self):
        row = self._stills_list.currentRow()
        if row >= 0:
            self._stills_list.takeItem(row)
            self._stills.pop(row)
            self._update_memory()

    def _update_memory(self):
        self._memory_label.setText(f"Memory: {len(self._stills)} stills")

    @staticmethod
    def _list_style():
        return """QListWidget { background-color: #222; border: 1px solid #333; border-radius: 4px; color: #888; font-size: 12px; outline: none; }
QListWidget::item:selected { background-color: #3a3a3a; color: #aaa; }"""

    @staticmethod
    def _button_style():
        return """QPushButton { background-color: #333; color: #888; border: 1px solid #444; border-radius: 4px; padding: 6px 16px; font-size: 12px; }
QPushButton:hover { background-color: #444; color: #aaa; }"""
