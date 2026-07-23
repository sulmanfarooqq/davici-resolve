"""Tracker panel: OpenCV-based point tracking."""

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QListWidget,
                               QPushButton, QSpinBox, QVBoxLayout, QWidget,
                               QProgressBar, QMessageBox)
from PySide6.QtCore import QThread


class _TrackWorker(QThread):
    progress = Signal(int)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, reader, start_frame, end_frame, bbox):
        super().__init__()
        self.reader = reader
        self.start = start_frame
        self.end = end_frame
        self.bbox = bbox
        self._cancel = False

    def run(self):
        import cv2
        results = []
        frame = self.reader.read_frame(self.start)
        if frame is None:
            self.error.emit("Could not read start frame")
            return
        tracker = cv2.TrackerCSRT_create()
        tracker.init(frame, self.bbox)
        results.append((self.start, self.bbox))

        total = abs(self.end - self.start)
        step = 1 if self.end >= self.start else -1
        for i, idx in enumerate(range(self.start + step, self.end + step, step)):
            if self._cancel:
                return
            frame = self.reader.read_frame(idx)
            if frame is None:
                break
            success, bbox = tracker.update(frame)
            if success:
                results.append((idx, bbox))
            self.progress.emit(int((i + 1) / total * 100))
        self.finished.emit(results)

    def cancel(self):
        self._cancel = True


class TrackerPanel(QWidget):
    track_data = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._reader = None
        self._bbox = None
        self._worker = None
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
        for text, cb in [("Track Forward", self._track_fwd), ("Track Backward", self._track_bwd)]:
            btn = QPushButton(text)
            btn.setStyleSheet(self._button_style())
            btn.clicked.connect(cb)
            track_row.addWidget(btn)
        layout.addLayout(track_row)

        self._progress = QProgressBar()
        self._progress.setVisible(False)
        self._progress.setStyleSheet("QProgressBar { background: #222; border: 1px solid #333; border-radius: 4px; height: 12px; text-align: center; color: #888; font-size: 10px; } QProgressBar::chunk { background: #4a4; }")
        layout.addWidget(self._progress)

        self._tracker_list = QListWidget()
        self._tracker_list.setStyleSheet(self._list_style())
        self._tracker_list.setMinimumHeight(80)
        layout.addWidget(self._tracker_list, 1)

        params_label = QLabel("Parameters")
        params_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(params_label)

        acc_row = QHBoxLayout()
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
        self._motion_blur.setStyleSheet("color: #888; font-size: 11px; spacing: 6px;")
        layout.addWidget(self._motion_blur)

        self._status = QLabel("Status: Idle")
        self._status.setStyleSheet("color: #666; font-size: 11px; padding: 4px 0;")
        layout.addWidget(self._status)
        layout.addStretch()

    def set_reader(self, reader):
        self._reader = reader

    def set_bbox(self, bbox):
        self._bbox = bbox

    def _track_fwd(self):
        self._start_track(1)

    def _track_bwd(self):
        self._start_track(-1)

    def _start_track(self, direction):
        if self._reader is None or not self._reader.is_open:
            QMessageBox.warning(self, "Error", "No video loaded")
            return
        if self._bbox is None:
            QMessageBox.warning(self, "Error", "No region selected. Right-click on viewer to select a tracking region.")
            return
        self._progress.setVisible(True)
        self._progress.setValue(0)
        self._status.setText("Status: Tracking...")
        start = self._reader.total_frames // 2
        end = self._reader.total_frames - 1 if direction > 0 else 0
        self._worker = _TrackWorker(self._reader, start, end, self._bbox)
        self._worker.progress.connect(self._progress.setValue)
        self._worker.finished.connect(self._on_track_done)
        self._worker.error.connect(lambda msg: QMessageBox.warning(self, "Error", msg))
        self._worker.start()

    def _on_track_done(self, results):
        self._progress.setVisible(False)
        self._status.setText(f"Status: Tracked {len(results)} frames")
        self._tracker_list.addItem(f"Track: {len(results)} frames")
        self.track_data.emit(results)

    def set_status(self, text):
        self._status.setText(f"Status: {text}")

    def add_tracker(self, name):
        self._tracker_list.addItem(name)

    @property
    def accuracy(self):
        return self._accuracy.value()

    @property
    def motion_blur_enabled(self):
        return self._motion_blur.isChecked()

    @staticmethod
    def _button_style():
        return """QPushButton { background-color: #333; color: #888; border: 1px solid #444; border-radius: 4px; padding: 8px 12px; font-size: 12px; }
QPushButton:hover { background-color: #444; color: #aaa; }"""

    @staticmethod
    def _list_style():
        return """QListWidget { background-color: #222; border: 1px solid #333; border-radius: 4px; color: #888; font-size: 12px; outline: none; }
QListWidget::item:selected { background-color: #3a3a3a; color: #aaa; }"""

    @staticmethod
    def _spinbox_style():
        return """QSpinBox { background-color: #222; color: #888; border: 1px solid #444; border-radius: 4px; padding: 4px 8px; font-size: 11px; }
QSpinBox::up-button, QSpinBox::down-button { background-color: #333; border: none; width: 16px; }
QSpinBox::up-arrow { image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-bottom: 5px solid #888; }
QSpinBox::down-arrow { image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid #888; }"""
