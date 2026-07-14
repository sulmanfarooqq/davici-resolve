from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class PowerWindowsPanel(QWidget):
    SHAPES = ["Circle", "Rectangle", "Gradient", "Curve"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_shape = None
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
        self._indicator.setStyleSheet(
            "color: #666; font-size: 11px; padding: 4px 0;"
        )
        layout.addWidget(self._indicator)

        for shape in self.SHAPES:
            btn = QPushButton(shape)
            btn.setStyleSheet(self._shape_button_style())
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, s=shape: self._select_shape(s)
            )
            layout.addWidget(btn)

        self._mask_list = QListWidget()
        self._mask_list.setStyleSheet(self._list_style())
        self._mask_list.setMinimumHeight(80)
        mask_size = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._mask_list.setSizePolicy(mask_size)
        layout.addWidget(self._mask_list)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        add_btn = QPushButton("Add Mask")
        add_btn.setStyleSheet(self._action_button_style())
        add_btn.clicked.connect(self._on_add_mask)
        btn_row.addWidget(add_btn)

        remove_btn = QPushButton("Remove Mask")
        remove_btn.setStyleSheet(self._action_button_style())
        remove_btn.clicked.connect(self._on_remove_mask)
        btn_row.addWidget(remove_btn)

        layout.addLayout(btn_row)

    def _select_shape(self, shape: str) -> None:
        self._active_shape = shape
        self._indicator.setText(f"Active Mask: {shape}")

    def _on_add_mask(self) -> None:
        if self._active_shape:
            self._mask_list.addItem(self._active_shape)

    def _on_remove_mask(self) -> None:
        row = self._mask_list.currentRow()
        if row >= 0:
            self._mask_list.takeItem(row)

    @staticmethod
    def _shape_button_style() -> str:
        return """
        QPushButton {
            background-color: #2a2a2a;
            color: #888;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 12px;
            text-align: left;
        }
        QPushButton:hover {
            background-color: #333;
            color: #aaa;
            border-color: #555;
        }
        QPushButton:pressed {
            background-color: #3a3a3a;
        }
        """

    @staticmethod
    def _action_button_style() -> str:
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
        """

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
