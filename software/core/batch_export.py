"""Batch export: apply current grade to multiple frames/images and export."""

import os
import numpy as np
from typing import Optional, Callable
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QFileDialog, QProgressBar, QCheckBox, QWidget,
)


class _ExportWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(int, str)
    error = Signal(str)

    def __init__(self, frames, grade_fn, output_dir, format_ext, quality):
        super().__init__()
        self.frames = frames
        self.grade_fn = grade_fn
        self.output_dir = output_dir
        self.format_ext = format_ext
        self.quality = quality
        self._cancel = False

    def run(self):
        from PIL import Image
        total = len(self.frames)
        for i, (frame_path, frame_data) in enumerate(self.frames):
            if self._cancel:
                break
            try:
                graded = self.grade_fn(frame_data)
                arr = np.clip(graded * 255.0, 0, 255).astype(np.uint8)
                base = os.path.splitext(os.path.basename(frame_path))[0]
                out_path = os.path.join(self.output_dir, f"{base}_graded.{self.format_ext}")
                img = Image.fromarray(arr)
                if self.format_ext.lower() == 'jpg':
                    img.save(out_path, quality=self.quality)
                elif self.format_ext.lower() == 'png':
                    img.save(out_path)
                elif self.format_ext.lower() in ('tif', 'tiff'):
                    img.save(out_path)
                else:
                    img.save(out_path)
                self.progress.emit(int((i + 1) / total * 100), out_path)
            except Exception as e:
                self.error.emit(str(e))
        self.finished.emit(total, self.output_dir)

    def cancel(self):
        self._cancel = True


class BatchExportDialog(QDialog):
    def __init__(self, grade_fn: Callable, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Export")
        self.setMinimumSize(500, 350)
        self.grade_fn = grade_fn
        self._frames = []
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Batch Export — Apply grade to multiple files")
        title.setStyleSheet("color: #ccc; font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        folder_row = QHBoxLayout()
        self._folder_label = QLabel("No folder selected")
        self._folder_label.setStyleSheet("color: #888; font-size: 11px;")
        folder_row.addWidget(self._folder_label, 1)
        browse_btn = QPushButton("Browse Folder")
        browse_btn.clicked.connect(self._browse_folder)
        folder_row.addWidget(browse_btn)
        layout.addLayout(folder_row)

        self._file_count = QLabel("Files: 0")
        self._file_count.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self._file_count)

        opt_row = QHBoxLayout()
        opt_row.addWidget(QLabel("Format:"))
        self._format = QComboBox()
        self._format.addItems(["png", "jpg", "tif"])
        opt_row.addWidget(self._format)
        opt_row.addWidget(QLabel("Quality:"))
        self._quality = QSpinBox()
        self._quality.setRange(1, 100)
        self._quality.setValue(95)
        opt_row.addWidget(self._quality)
        self._overwrite = QCheckBox("Overwrite existing")
        opt_row.addWidget(self._overwrite)
        opt_row.addStretch()
        layout.addLayout(opt_row)

        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._status = QLabel("")
        self._status.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self._status)

        btn_row = QHBoxLayout()
        self._export_btn = QPushButton("Export All")
        self._export_btn.clicked.connect(self._start_export)
        btn_row.addWidget(self._export_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._cancel_export)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self._load_folder(folder)

    def _load_folder(self, folder):
        exts = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.exr', '.dpx'}
        self._frames = []
        for f in sorted(os.listdir(folder)):
            if os.path.splitext(f)[1].lower() in exts:
                self._frames.append(os.path.join(folder, f))
        self._folder_label.setText(folder)
        self._file_count.setText(f"Files: {len(self._frames)}")

    def _start_export(self):
        if not self._frames:
            self._status.setText("No files loaded")
            return
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not output_dir:
            return
        self._progress.setVisible(True)
        self._progress.setValue(0)
        self._export_btn.setEnabled(False)
        self._status.setText("Loading and grading frames...")

        from PIL import Image
        frame_data = []
        for path in self._frames:
            try:
                img = Image.open(path).convert('RGB')
                arr = np.array(img, dtype=np.float32) / 255.0
                frame_data.append((path, arr))
            except Exception:
                continue

        self._worker = _ExportWorker(
            frame_data, self.grade_fn, output_dir,
            self._format.currentText(), self._quality.value()
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(lambda msg: self._status.setText(f"Error: {msg}"))
        self._worker.start()

    def _cancel_export(self):
        if self._worker:
            self._worker.cancel()

    def _on_progress(self, pct, path):
        self._progress.setValue(pct)
        self._status.setText(f"Exported: {os.path.basename(path)}")

    def _on_finished(self, count, folder):
        self._progress.setVisible(False)
        self._export_btn.setEnabled(True)
        self._status.setText(f"Done! Exported {count} files to {folder}")
