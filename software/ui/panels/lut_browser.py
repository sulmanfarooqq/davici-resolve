"""LUT Browser panel: scan directories for .cube files and apply on click."""

import os
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                               QPushButton, QSizePolicy, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout, QWidget, QFileDialog)
from core.lut_parser import parse_cube, cube_to_lut3d, apply_lut_3d


class LUTBrowserPanel(QWidget):
    lut_applied = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._luts = {}
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: #1a1a1a;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        title = QLabel("LUT Browser")
        title.setStyleSheet("color: #888; font-size: 13px; font-weight: bold;")
        layout.addWidget(title)
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search LUTs...")
        self._search.setStyleSheet(self._search_style())
        self._search.textChanged.connect(self._on_search)
        layout.addWidget(self._search)
        self._tree = QTreeWidget()
        self._tree.setColumnCount(3)
        self._tree.setHeaderLabels(["Name", "Size", "Type"])
        self._tree.setStyleSheet(self._tree_style())
        self._tree.setAlternatingRowColors(True)
        self._tree.setRootIsDecorated(False)
        self._tree.setSortingEnabled(True)
        self._tree.setMinimumHeight(180)
        self._tree.itemDoubleClicked.connect(lambda: self._on_apply())
        tree_size = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tree.setSizePolicy(tree_size)
        header = self._tree.header()
        header.setStretchLastSection(True)
        for i in range(3):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        layout.addWidget(self._tree)
        self._status_label = QLabel("Folder: <not scanned>")
        self._status_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self._status_label)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        for text, cb in [("Apply", self._on_apply), ("Scan Folder", self._on_scan)]:
            btn = QPushButton(text)
            btn.setStyleSheet(self._button_style())
            btn.clicked.connect(cb)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

    def _on_search(self, text):
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            match = text.lower() in item.text(0).lower()
            item.setHidden(not match)

    def _on_apply(self):
        items = self._tree.selectedItems()
        if not items:
            return
        name = items[0].text(0)
        path = self._luts.get(name)
        if path and os.path.exists(path):
            lut = cube_to_lut3d(path)
            if lut is not None:
                self.lut_applied.emit(lut)
                self._status_label.setText(f"Applied: {name}")

    def _on_scan(self):
        folder = QFileDialog.getExistingDirectory(self, "Scan LUT Folder")
        if not folder:
            return
        self._tree.clear()
        self._luts.clear()
        count = 0
        for root, dirs, files in os.walk(folder):
            for f in sorted(files):
                if f.lower().endswith('.cube'):
                    path = os.path.join(root, f)
                    try:
                        data = parse_cube(path)
                        size = str(data['size'])
                        ltype = data['type']
                        name = os.path.splitext(f)[0]
                        self._luts[name] = path
                        self.add_lut(name, size, ltype)
                        count += 1
                    except Exception:
                        pass
        self._status_label.setText(f"Folder: {folder} — {count} LUTs found")

    def add_lut(self, name, size, lut_type):
        item = QTreeWidgetItem([name, size, lut_type])
        self._tree.addTopLevelItem(item)

    def clear(self):
        self._tree.clear()

    def selected_lut(self):
        items = self._tree.selectedItems()
        if items:
            return items[0].text(0)
        return None

    @staticmethod
    def _search_style():
        return """QLineEdit { background-color: #222; color: #888; border: 1px solid #444; border-radius: 4px; padding: 6px 10px; font-size: 12px; }
QLineEdit:focus { border-color: #666; }"""

    @staticmethod
    def _tree_style():
        return """QTreeWidget { background-color: #222; alternate-background-color: #252525; border: 1px solid #333; border-radius: 4px; color: #888; font-size: 12px; outline: none; }
QTreeWidget::item:selected { background-color: #3a3a3a; color: #aaa; }
QHeaderView::section { background-color: #2a2a2a; color: #888; border: none; border-bottom: 1px solid #444; padding: 6px 8px; font-size: 11px; }"""

    @staticmethod
    def _button_style():
        return """QPushButton { background-color: #333; color: #888; border: 1px solid #444; border-radius: 4px; padding: 6px 16px; font-size: 12px; }
QPushButton:hover { background-color: #444; color: #aaa; }"""
