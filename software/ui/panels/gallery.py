from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class GalleryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._memory_used = 0
        self._memory_max = 100
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
        list_size = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._stills_list.setSizePolicy(list_size)
        layout.addWidget(self._stills_list)

        preview_area = QWidget()
        preview_area.setFixedHeight(80)
        preview_area.setStyleSheet(
            "background-color: #222; border: 1px solid #333; border-radius: 4px;"
        )
        preview_layout = QVBoxLayout(preview_area)
        preview_layout.setAlignment(Qt.AlignCenter)
        preview_label = QLabel("Thumbnail Preview")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_label.setStyleSheet("color: #555; font-size: 11px; border: none;")
        preview_layout.addWidget(preview_label)
        layout.addWidget(preview_area)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(self._button_style())
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        load_btn = QPushButton("Load")
        load_btn.setStyleSheet(self._button_style())
        load_btn.clicked.connect(self._on_load)
        btn_row.addWidget(load_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet(self._button_style())
        delete_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(delete_btn)

        layout.addLayout(btn_row)

        self._memory_label = QLabel(self._memory_text())
        self._memory_label.setStyleSheet(
            "color: #666; font-size: 11px; padding: 2px 0;"
        )
        layout.addWidget(self._memory_label)

    def _on_save(self) -> None:
        pass

    def _on_load(self) -> None:
        pass

    def _on_delete(self) -> None:
        row = self._stills_list.currentRow()
        if row >= 0:
            self._stills_list.takeItem(row)
            self._update_memory()

    def add_still(self, name: str) -> None:
        if self._memory_used < self._memory_max:
            item = QListWidgetItem(name)
            self._stills_list.addItem(item)
            self._memory_used += 1
            self._update_memory()

    def _update_memory(self) -> None:
        self._memory_label.setText(self._memory_text())

    def _memory_text(self) -> str:
        return f"Memory: {self._memory_used}/{self._memory_max}"

    @property
    def memory_used(self) -> int:
        return self._memory_used

    @property
    def memory_max(self) -> int:
        return self._memory_max

    @staticmethod
    def _list_style() -> str:
        return """
        QListWidget {
            background-color: #222;
            border: 1px solid #333;
            border-radius: 4px;
            color: #888;
            font-size: 12px;
            outline: none;
        }
        QListWidget::item:selected {
            background-color: #3a3a3a;
            color: #aaa;
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
