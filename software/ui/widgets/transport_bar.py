"""Transport controls: play/pause, frame stepping, speed, frame counter."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PySide6.QtCore import Signal, Qt


class TransportBar(QWidget):
    play_pause_clicked = Signal()
    stop_clicked = Signal()
    step_forward_clicked = Signal()
    step_backward_clicked = Signal()
    speed_changed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)
        self.setStyleSheet("background-color: #1a1a1e;")
        self._playing = False
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        self._prev_btn = QPushButton("|<")
        self._prev_btn.setFixedSize(28, 26)
        self._prev_btn.clicked.connect(self.step_backward_clicked.emit)

        self._play_btn = QPushButton("▶")
        self._play_btn.setFixedSize(28, 26)
        self._play_btn.clicked.connect(self._on_play_pause)

        self._next_btn = QPushButton(">|")
        self._next_btn.setFixedSize(28, 26)
        self._next_btn.clicked.connect(self.step_forward_clicked.emit)

        self._stop_btn = QPushButton("■")
        self._stop_btn.setFixedSize(28, 26)
        self._stop_btn.clicked.connect(self.stop_clicked.emit)

        self._frame_label = QLabel("0 / 0")
        self._frame_label.setFixedWidth(100)
        self._frame_label.setStyleSheet("color: #aaa; font-family: monospace;")

        self._speed_combo = QComboBox()
        self._speed_combo.addItems(["0.25x", "0.5x", "1x", "2x", "4x"])
        self._speed_combo.setCurrentText("1x")
        self._speed_combo.setFixedWidth(64)
        self._speed_combo.currentTextChanged.connect(self._on_speed_changed)

        layout.addWidget(self._prev_btn)
        layout.addWidget(self._play_btn)
        layout.addWidget(self._next_btn)
        layout.addWidget(self._stop_btn)
        layout.addWidget(self._frame_label)
        layout.addStretch()
        layout.addWidget(QLabel("Speed:"))
        layout.addWidget(self._speed_combo)

    def _on_play_pause(self):
        self._playing = not self._playing
        self._play_btn.setText("⏸" if self._playing else "▶")
        self.play_pause_clicked.emit()

    def set_playing(self, playing: bool):
        self._playing = playing
        self._play_btn.setText("⏸" if playing else "▶")

    def update_frame_info(self, current: int, total: int):
        self._frame_label.setText(f"{current} / {total}")

    def _on_speed_changed(self, text: str):
        speed = float(text.replace("x", ""))
        self.speed_changed.emit(speed)
