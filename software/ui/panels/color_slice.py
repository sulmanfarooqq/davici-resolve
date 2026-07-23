"""6-vector color slice panel: RGB and CMY sliders wired to CDL grading."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QPushButton, QWidget
from core.color_math import colorbalance_cdl


class ColorSlicePanel(QWidget):
    values_changed = Signal(dict)

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

        colors = [("#ff6666", "R"), ("#66ff66", "G"), ("#6666ff", "B"),
                  ("#66ffff", "C"), ("#ff66ff", "M"), ("#ffff66", "Y")]
        for color_hex, ch in colors:
            row = QHBoxLayout()
            row.setSpacing(8)
            label = QLabel(ch)
            label.setFixedWidth(20)
            label.setStyleSheet(f"color: {color_hex}; font-weight: bold;")
            label.setAlignment(Qt.AlignCenter)
            row.addWidget(label)
            slider = QSlider(Qt.Horizontal)
            slider.setRange(-1000, 1000)
            slider.setValue(0)
            slider.setStyleSheet(self._slider_style())
            row.addWidget(slider)
            value_label = QLabel("0.00")
            value_label.setFixedWidth(40)
            value_label.setStyleSheet("color: #aaa; font-family: monospace;")
            value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.addWidget(value_label)
            def make_cb(k=ch, vl=value_label):
                def cb(v):
                    vl.setText(f"{int(v)/1000.0:+.2f}")
                    self._emit_values()
                return cb
            slider.valueChanged.connect(make_cb())
            self._sliders[ch] = slider
            layout.addLayout(row)

        layout.addStretch()
        reset_btn = QPushButton("Reset")
        reset_btn.setStyleSheet(self._button_style())
        reset_btn.clicked.connect(self.reset)
        layout.addWidget(reset_btn)

    def _emit_values(self):
        vals = {k: int(s.value()) / 1000.0 for k, s in self._sliders.items()}
        self.values_changed.emit(vals)

    def get_values(self):
        return {k: int(s.value()) / 1000.0 for k, s in self._sliders.items()}

    def set_values(self, vals: dict):
        for k, v in vals.items():
            if k in self._sliders:
                self._sliders[k].setValue(int(v * 1000))

    def reset(self):
        for s in self._sliders.values():
            s.setValue(0)

    def apply_to_image(self, img):
        vals = self.get_values()
        slope = [1.0, 1.0, 1.0]
        offset = [0.0, 0.0, 0.0]
        slope[0] = max(0.01, 1.0 + vals.get("R", 0))
        slope[1] = max(0.01, 1.0 + vals.get("G", 0))
        slope[2] = max(0.01, 1.0 + vals.get("B", 0))
        offset[0] = -vals.get("C", 0) * 0.1
        offset[1] = -vals.get("M", 0) * 0.1
        offset[2] = -vals.get("Y", 0) * 0.1
        return colorbalance_cdl(img, slope, offset, [1.0, 1.0, 1.0])

    @staticmethod
    def _slider_style():
        return """QSlider::groove:horizontal { background: #2a2a2a; height: 6px; border-radius: 3px; }
QSlider::handle:horizontal { background: #555; width: 14px; height: 14px; margin: -4px 0; border-radius: 7px; }
QSlider::handle:horizontal:hover { background: #777; }
QSlider::sub-page:horizontal { background: #555; border-radius: 3px; }"""

    @staticmethod
    def _button_style():
        return "QPushButton { background-color: #333; color: #888; border: 1px solid #444; border-radius: 4px; padding: 6px 16px; font-size: 12px; } QPushButton:hover { background-color: #444; color: #aaa; }"
