from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class ColorSlicePanel(QWidget):
    CHANNELS = ["R", "G", "B", "C", "M", "Y"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sliders = {}
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: #1a1a1a;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        title = QLabel("6-Vector Color Wheels")
        title.setStyleSheet("color: #888; font-size: 13px; font-weight: bold;")
        layout.addWidget(title)

        for ch in self.CHANNELS:
            row = QHBoxLayout()
            row.setSpacing(8)

            label = QLabel(ch)
            label.setFixedWidth(20)
            label.setStyleSheet("color: #888; font-weight: bold;")
            label.setAlignment(Qt.AlignCenter)
            row.addWidget(label)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(-100, 100)
            slider.setValue(0)
            slider.setStyleSheet(self._slider_style())
            row.addWidget(slider)

            value_label = QLabel("0")
            value_label.setFixedWidth(36)
            value_label.setStyleSheet("color: #888;")
            value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.addWidget(value_label)

            slider.valueChanged.connect(
                lambda v, vl=value_label: vl.setText(str(v))
            )

            self._sliders[ch] = slider
            layout.addLayout(row)

        layout.addStretch()

    def get_values(self) -> dict[str, int]:
        return {ch: s.value() for ch, s in self._sliders.items()}

    def set_values(self, values: dict[str, int]) -> None:
        for ch, v in values.items():
            if ch in self._sliders:
                self._sliders[ch].setValue(v)

    def reset(self) -> None:
        for s in self._sliders.values():
            s.setValue(0)

    @staticmethod
    def _slider_style() -> str:
        return """
        QSlider::groove:horizontal {
            background: #2a2a2a;
            height: 6px;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #555;
            width: 14px;
            height: 14px;
            margin: -4px 0;
            border-radius: 7px;
        }
        QSlider::handle:horizontal:hover {
            background: #777;
        }
        QSlider::sub-page:horizontal {
            background: #555;
            border-radius: 3px;
        }
        """
