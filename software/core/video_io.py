"""Video IO wrapper using OpenCV with batch reading support."""

import cv2
import numpy as np
from typing import Optional, List


class VideoReader:
    def __init__(self):
        self._cap: Optional[cv2.VideoCapture] = None
        self.path: str = ""
        self.total_frames: int = 0
        self.fps: float = 24.0
        self.duration_sec: float = 0.0
        self.width: int = 0
        self.height: int = 0

    @property
    def is_open(self) -> bool:
        return self._cap is not None

    def open(self, path: str) -> bool:
        self._cap = cv2.VideoCapture(path)
        if not self._cap.isOpened():
            self._cap = None
            return False
        self.path = path
        self.total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self._cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0:
            self.fps = 24.0
        self.duration_sec = self.total_frames / self.fps if self.fps > 0 else 0.0
        self.width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return True

    def read_frame(self, index: int) -> Optional[np.ndarray]:
        if self._cap is None:
            return None
        index = max(0, min(index, self.total_frames - 1))
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = self._cap.read()
        if not ret:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def read_frame_batch(self, start: int, count: int) -> List[np.ndarray]:
        if self._cap is None or count < 1:
            return []
        start = max(0, min(start, self.total_frames - 1))
        count = min(count, self.total_frames - start)
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, start)
        frames = []
        for _ in range(count):
            ret, frame = self._cap.read()
            if not ret:
                break
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        return frames

    def close(self):
        if self._cap:
            self._cap.release()
            self._cap = None
        self.path = ""
