from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)


class InfoPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: #1a1a1a;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        image_title = QLabel("Image Info")
        image_title.setStyleSheet(
            "color: #888; font-size: 13px; font-weight: bold;"
        )
        layout.addWidget(image_title)

        self._image_info = QLabel()
        self._image_info.setStyleSheet(
            "color: #888; font-size: 11px; padding: 4px 0;"
        )
        self._image_info.setText(
            "Dimensions: -\n"
            "Bit Depth: -\n"
            "Color Space: -\n"
            "FPS: -"
        )
        layout.addWidget(self._image_info)

        cursor_title = QLabel("Cursor Info")
        cursor_title.setStyleSheet(
            "color: #888; font-size: 13px; font-weight: bold; padding-top: 8px;"
        )
        layout.addWidget(cursor_title)

        self._cursor_info = QLabel()
        self._cursor_info.setStyleSheet(
            "color: #888; font-size: 11px; padding: 4px 0;"
        )
        self._cursor_info.setText(
            "Position: -\n"
            "RGB: -\n"
            "HSV: -"
        )
        layout.addWidget(self._cursor_info)

        layout.addStretch()

    def update_image_info(self, info: dict) -> None:
        lines = []
        lines.append(f"Dimensions: {info.get('dimensions', '-')}")
        lines.append(f"Bit Depth: {info.get('bit_depth', '-')}")
        lines.append(f"Color Space: {info.get('color_space', '-')}")
        lines.append(f"FPS: {info.get('fps', '-')}")
        self._image_info.setText("\n".join(lines))

    def update_cursor_info(self, info: dict) -> None:
        lines = []
        lines.append(f"Position: {info.get('position', '-')}")
        lines.append(f"RGB: {info.get('rgb', '-')}")
        lines.append(f"HSV: {info.get('hsv', '-')}")
        self._cursor_info.setText("\n".join(lines))
