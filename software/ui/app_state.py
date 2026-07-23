"""Application state singleton."""

from PySide6.QtCore import QObject, Signal
from typing import Optional


class AppState(QObject):
    grade_changed = Signal()
    frame_changed = Signal(int)
    node_graph_changed = Signal()

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True
        self.video_path: Optional[str] = None
        self.current_frame_index: int = 0
        self.total_frames: int = 0
        self.fps: float = 24.0
        self.frame_width: int = 1920
        self.frame_height: int = 1080
        self.is_playing: bool = False
        self.current_frame_rgb = None
        self.colorspace: str = "srgb"
