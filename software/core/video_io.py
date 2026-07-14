"""Video IO wrapper using OpenCV."""

import cv2
import numpy as np
from typing import Optional


class VideoReader:
    def __init__(self):
        self._cap: Optional[cv2.VideoCapture] = None
        self.path: str = ""
        self.total_frames: int = 0
        self.fps: float = 24.0
        self.width: int = 0
        self.height: int = 0

    def open(self, path: str) -> bool:
        self._cap = cv2.VideoCapture(path)
        if not self._cap.isOpened():
            return False
        self.path = path
        self.total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self._cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return True

    def read_frame(self, index: int) -> Optional[np.ndarray]:
        if self._cap is None:
            return None
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = self._cap.read()
        if not ret:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def close(self):
        if self._cap:
            self._cap.release()
            self._cap = None
        self.path = ""
