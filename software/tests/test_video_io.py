import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import tempfile, os
import numpy as np
import cv2
from core.video_io import VideoReader

def _make_test_video(path, num_frames=10, width=64, height=48, fps=24.0):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(path, fourcc, fps, (width, height))
    for i in range(num_frames):
        frame = np.full((height, width, 3), i / num_frames, dtype=np.float32)
        writer.write((frame * 255).astype(np.uint8))
    writer.release()

def test_video_reader_init():
    r = VideoReader()
    assert r.path == ""
    assert r.total_frames == 0
    assert r.fps == 24.0

def test_video_reader_open_nonexistent():
    r = VideoReader()
    assert r.open("/nonexistent/video.mp4") is False

def test_video_reader_open_and_read():
    f = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    f.close()
    try:
        _make_test_video(f.name, num_frames=10, width=64, height=48)
        r = VideoReader()
        assert r.open(f.name) is True
        assert r.total_frames == 10
        assert r.fps == 24.0
        assert r.width == 64
        assert r.height == 48
        frame = r.read_frame(0)
        assert frame is not None
        assert frame.shape == (48, 64, 3)
        assert frame.dtype == np.uint8
        r.close()
        assert r.path == ""
    finally:
        os.unlink(f.name)

def test_video_reader_read_all_frames():
    f = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    f.close()
    try:
        _make_test_video(f.name, num_frames=5, width=32, height=24)
        r = VideoReader()
        r.open(f.name)
        for i in range(5):
            frame = r.read_frame(i)
            assert frame is not None
            assert frame.shape == (24, 32, 3)
        assert r.read_frame(999) is None
        r.close()
    finally:
        os.unlink(f.name)

def test_video_reader_close_twice():
    r = VideoReader()
    r.close()
    assert r.path == ""

def test_video_reader_read_before_open():
    r = VideoReader()
    assert r.read_frame(0) is None
