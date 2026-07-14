"""Simple LRU frame cache."""

import numpy as np
from collections import OrderedDict
from typing import Optional


class FrameCache:
    def __init__(self, max_frames: int = 120):
        self._cache: OrderedDict[int, np.ndarray] = OrderedDict()
        self._max = max_frames

    def get(self, index: int) -> Optional[np.ndarray]:
        if index in self._cache:
            self._cache.move_to_end(index)
            return self._cache[index]
        return None

    def put(self, index: int, frame: np.ndarray):
        self._cache[index] = frame
        if len(self._cache) > self._max:
            self._cache.popitem(last=False)

    def clear(self):
        self._cache.clear()
