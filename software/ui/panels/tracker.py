from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class TrackerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: #1a1a1a;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("Tracker")
        title.setStyleSheet("color: #888; font-size: 13px; font-weight: bold;")
        layout.addWidget(title)

        track_row = QHBoxLayout()
        track_row.setSpacing(8)

        fwd_btn = QPushButton("Track Forward")
        fwd_btn.setStyleSheet(self._button_style())
        track_row.addWidget(fwd_btn)

        bwd_btn = QPushButton("Track Backward")
        bwd_btn.setStyleSheet(self._button_style())
        track_row.addWidget(bwd_btn)

        layout.addLayout(track_row)

        self._tracker_list = QListWidget()
        self._tracker_list.setStyleSheet(self._list_style())
        self._tracker_list.setMinimumHeight(100)
        list_size = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._tracker_list.setSizePolicy(list_size)
        layout.addWidget(self._tracker_list)

        params_label = QLabel("Parameters")
        params_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(params_label)

        acc_row = QHBoxLayout()
        acc_row.setSpacing(8)

        acc_label = QLabel("Accuracy:")
        acc_label.setStyleSheet("color: #888; font-size: 11px;")
        acc_row.addWidget(acc_label)

        self._accuracy = QSpinBox()
        self._accuracy.setRange(1, 100)
        self._accuracy.setValue(50)
        self._accuracy.setStyleSheet(self._spinbox_style())
        acc_row.addWidget(self._accuracy)

        layout.addLayout(acc_row)

        self._motion_blur = QCheckBox("Motion Blur")
        self._motion_blur.setStyleSheet(
            "color: #888; font-size: 11px; spacing: 6px;"
        )
        layout.addWidget(self._motion_blur)

        self._status = QLabel("Status: Idle")
        self._status.setStyleSheet(
            "color: #666; font-size: 11px; padding: 4px 0;"
        )
        layout.addWidget(self._status)

        layout.addStretch()

    def set_status(self, text: str) -> None:
        self._status.setText(f"Status: {text}")

    def add_tracker(self, name: str) -> None:
        self._tracker_list.addItem(name)

    @property
    def accuracy(self) -> int:
        return self._accuracy.value()

    @property
    def motion_blur_enabled(self) -> bool:
        return self._motion_blur.isChecked()

    @staticmethod
    def _button_style() -> str:
        return """
        QPushButton {
            background-color: #333;
            color: #888;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 8px 12px;
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
    def _spinbox_style() -> str:
        return """
        QSpinBox {
            background-color: #222;
            color: #888;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 11px;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #333;
            border: none;
            width: 16px;
        }
        QSpinBox::up-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: 5px solid #888;
        }
        QSpinBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid #888;
        }
        """
