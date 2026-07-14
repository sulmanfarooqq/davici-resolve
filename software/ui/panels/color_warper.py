from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ColorWarperPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: #1a1a1a;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("Color Warper")
        title.setStyleSheet("color: #888; font-size: 13px; font-weight: bold;")
        layout.addWidget(title)

        canvas = QWidget()
        canvas.setMinimumHeight(240)
        canvas.setStyleSheet(
            "background-color: #222; border: 1px solid #333; border-radius: 4px;"
        )
        canvas_size = QSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        canvas.setSizePolicy(canvas_size)

        canvas_layout = QVBoxLayout(canvas)
        canvas_layout.setAlignment(Qt.AlignCenter)
        placeholder = QLabel("Grid-based color deformation (coming soon)")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #555; font-size: 12px; border: none;")
        canvas_layout.addWidget(placeholder)

        layout.addWidget(canvas)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        accept_btn = QPushButton("Accept")
        accept_btn.setStyleSheet(self._button_style())
        btn_row.addWidget(accept_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.setStyleSheet(self._button_style())
        btn_row.addWidget(reset_btn)

        reset_btn.clicked.connect(self._on_reset)
        layout.addLayout(btn_row)

    def _on_reset(self) -> None:
        pass

    @staticmethod
    def _button_style() -> str:
        return """
        QPushButton {
            background-color: #333;
            color: #888;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 6px 20px;
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
