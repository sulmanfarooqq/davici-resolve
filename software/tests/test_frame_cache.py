import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import numpy as np
from core.frame_cache import FrameCache

def _frame(index):
    return np.full((10, 10, 3), index, dtype=np.float32)

def test_cache_init():
    c = FrameCache(max_frames=5)
    assert c._max == 5
    assert len(c._cache) == 0

def test_cache_put_and_get():
    c = FrameCache(max_frames=10)
    f0 = _frame(0)
    c.put(0, f0)
    assert c.get(0) is f0

def test_cache_get_missing():
    c = FrameCache(max_frames=10)
    assert c.get(42) is None

def test_cache_lru_eviction():
    c = FrameCache(max_frames=3)
    for i in range(3):
        c.put(i, _frame(i))
    assert c.get(0) is not None
    assert c.get(1) is not None
    assert c.get(2) is not None
    c.put(3, _frame(3))
    assert c.get(3) is not None
    assert c.get(0) is None
    c.put(4, _frame(4))
    assert c.get(4) is not None
    assert c.get(1) is None

def test_cache_lru_order():
    c = FrameCache(max_frames=2)
    c.put(0, _frame(0))
    c.put(1, _frame(1))
    c.get(0)
    c.put(2, _frame(2))
    assert c.get(0) is not None
    assert c.get(1) is None

def test_cache_clear():
    c = FrameCache(max_frames=10)
    for i in range(5):
        c.put(i, _frame(i))
    c.clear()
    assert len(c._cache) == 0
    for i in range(5):
        assert c.get(i) is None

def test_cache_overwrite():
    c = FrameCache(max_frames=10)
    c.put(0, _frame(0))
    f1 = _frame(1)
    c.put(0, f1)
    assert c.get(0) is f1
