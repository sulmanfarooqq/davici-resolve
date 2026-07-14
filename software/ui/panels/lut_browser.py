from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class LUTBrowserPanel(QWidget):
    COLUMNS = ["Name", "Size", "Type"]

    def __init__(self, parent=None):
        super().__init__(parent)
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
        self._tree.setColumnCount(len(self.COLUMNS))
        self._tree.setHeaderLabels(self.COLUMNS)
        self._tree.setStyleSheet(self._tree_style())
        self._tree.setAlternatingRowColors(True)
        self._tree.setRootIsDecorated(False)
        self._tree.setSortingEnabled(True)
        self._tree.setMinimumHeight(180)
        tree_size = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tree.setSizePolicy(tree_size)

        header = self._tree.header()
        header.setStretchLastSection(True)
        for i in range(len(self.COLUMNS)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        layout.addWidget(self._tree)

        status_label = QLabel("Folder: <not scanned>")
        status_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(status_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet(self._button_style())
        apply_btn.clicked.connect(self._on_apply)
        btn_row.addWidget(apply_btn)

        scan_btn = QPushButton("Scan Folder")
        scan_btn.setStyleSheet(self._button_style())
        scan_btn.clicked.connect(self._on_scan)
        btn_row.addWidget(scan_btn)

        layout.addLayout(btn_row)

    def _on_search(self, text: str) -> None:
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            match = text.lower() in item.text(0).lower()
            item.setHidden(not match)

    def _on_apply(self) -> None:
        pass

    def _on_scan(self) -> None:
        pass

    def add_lut(self, name: str, size: str, lut_type: str) -> None:
        item = QTreeWidgetItem([name, size, lut_type])
        self._tree.addTopLevelItem(item)

    def clear(self) -> None:
        self._tree.clear()

    def selected_lut(self) -> str | None:
        items = self._tree.selectedItems()
        if items:
            return items[0].text(0)
        return None

    @staticmethod
    def _search_style() -> str:
        return """
        QLineEdit {
            background-color: #222;
            color: #888;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 12px;
        }
        QLineEdit:focus {
            border-color: #666;
        }
        """

    @staticmethod
    def _tree_style() -> str:
        return """
        QTreeWidget {
            background-color: #222;
            alternate-background-color: #252525;
            border: 1px solid #333;
            border-radius: 4px;
            color: #888;
            font-size: 12px;
            outline: none;
        }
        QTreeWidget::item:selected {
            background-color: #3a3a3a;
            color: #aaa;
        }
        QTreeWidget::item:hover {
            background-color: #2a2a2a;
        }
        QHeaderView::section {
            background-color: #2a2a2a;
            color: #888;
            border: none;
            border-bottom: 1px solid #444;
            padding: 6px 8px;
            font-size: 11px;
        }
        """

    @staticmethod
    def _button_style() -> str:
        return """
        QPushButton {
            background-color: #333;
            color: #888;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 6px 16px;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #444;
            color: #aaa;
        }
        QPushButton:pressed {
            background-color: #555;
        }
        """
