"""Playback controller with background decoding thread.

Uses a QThread to decode frames in the background, feeding them
into a bounded queue for lock-free readout by the main thread.
"""

from enum import Enum
from typing import Optional
import numpy as np
from PySide6.QtCore import QObject, QThread, Signal, QTimer


class PlaybackState(Enum):
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2


class DecodeWorker(QThread):
    frame_decoded = Signal(int, object)

    def __init__(self, reader, cache, parent=None):
        super().__init__(parent)
        self.reader = reader
        self.cache = cache
        self._running = False
        self._seek_target = -1
        self._direction = 1
        self._speed = 1.0
        self._skip_interval = 1

    def seek(self, frame_index: int):
        if self.reader is None or not self.reader.is_open:
            return
        self._seek_target = max(0, min(frame_index, self.reader.total_frames - 1))

    def set_speed(self, speed: float):
        self._speed = max(0.1, min(speed, 8.0))
        self._skip_interval = max(1, int(self._speed))

    def run(self):
        self._running = True
        current = 0
        while self._running:
            if self._seek_target >= 0:
                current = self._seek_target
                self._seek_target = -1

            if self.reader is None or not self.reader.is_open:
                break
            if current < 0 or current >= self.reader.total_frames:
                self._running = False
                break

            frame = self.cache.get(current)
            if frame is None:
                frame = self.reader.read_frame(current)
                if frame is not None:
                    self.cache.put(current, frame)
            if frame is not None:
                self.frame_decoded.emit(current, frame)

            base_sleep = 1000.0 / max(self.reader.fps, 1.0)
            sleep_ms = int(base_sleep / max(self._speed, 0.1))
            self.msleep(max(1, sleep_ms))

            current += self._skip_interval * self._direction

            if current >= self.reader.total_frames or current < 0:
                self._running = False
                break

    def stop(self):
        self._running = False
        self.wait()


class PlaybackController(QObject):
    state_changed = Signal(PlaybackState)
    frame_changed = Signal(int)
    position_changed = Signal(float)
    duration_changed = Signal(float)
    frame_ready = Signal(int, object)

    def __init__(self, reader, cache, parent=None):
        super().__init__(parent)
        self.reader = reader
        self.cache = cache
        self._state = PlaybackState.STOPPED
        self._current_frame: int = 0
        self._worker: Optional[DecodeWorker] = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(16)

    @property
    def state(self) -> PlaybackState:
        return self._state

    @property
    def current_frame(self) -> int:
        return self._current_frame

    @property
    def position(self) -> float:
        if self.reader.total_frames < 2:
            return 0.0
        return self._current_frame / (self.reader.total_frames - 1)

    def play(self):
        if self._state == PlaybackState.PLAYING:
            return
        if not self.reader.is_open or self.reader.total_frames < 1:
            return
        self._state = PlaybackState.PLAYING
        self._start_worker()
        self._timer.start()
        self.state_changed.emit(self._state)

    def pause(self):
        if self._state != PlaybackState.PLAYING:
            return
        self._state = PlaybackState.PAUSED
        self._stop_worker()
        self._timer.stop()
        self.state_changed.emit(self._state)

    def stop(self):
        self._state = PlaybackState.STOPPED
        self._stop_worker()
        self._timer.stop()
        self._current_frame = 0
        self.state_changed.emit(self._state)
        self.frame_changed.emit(0)

    def seek(self, frame_index: int):
        if not self.reader.is_open:
            return
        self._current_frame = max(0, min(frame_index, self.reader.total_frames - 1))
        if self._worker and self._worker.isRunning():
            self._worker.seek(self._current_frame)
        self.frame_changed.emit(self._current_frame)
        self.position_changed.emit(self.position)
        frame = self.cache.get(self._current_frame)
        if frame is not None:
            self.frame_ready.emit(self._current_frame, frame)

    def step_forward(self):
        self.seek(self._current_frame + 1)

    def step_backward(self):
        self.seek(self._current_frame - 1)

    def set_speed(self, speed: float):
        if self._worker and self._worker.isRunning():
            self._worker.set_speed(speed)

    def _start_worker(self):
        self._stop_worker()
        self._worker = DecodeWorker(self.reader, self.cache)
        self._worker.frame_decoded.connect(self._on_frame_decoded)
        self._worker.seek(self._current_frame)
        self._worker.start()

    def _stop_worker(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
        self._worker = None

    def _on_frame_decoded(self, index: int, frame: np.ndarray):
        self._current_frame = index
        self.frame_ready.emit(index, frame)
        self.frame_changed.emit(index)
        self.position_changed.emit(self.position)

    def _tick(self):
        if self._state == PlaybackState.PLAYING and self._current_frame >= self.reader.total_frames - 1:
            self.stop()
