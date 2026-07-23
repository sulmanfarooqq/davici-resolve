import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import pytest
pyside6 = pytest.importorskip("PySide6")
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from core.playback_controller import PlaybackController, PlaybackState
from core.frame_cache import FrameCache


class MockReader:
    is_open = True
    total_frames = 100
    fps = 24.0
    duration_sec = 100 / 24.0
    width = 64
    height = 48

    def read_frame(self, index):
        return np.full((48, 64, 3), index / 100, dtype=np.uint8)

    def read_frame_batch(self, start, count):
        return [self.read_frame(i) for i in range(start, start + count)]


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def _make_controller():
    reader = MockReader()
    cache = FrameCache(max_frames=30)
    ctrl = PlaybackController(reader, cache)
    return ctrl, reader, cache


def test_initial_state(qapp):
    ctrl, _, _ = _make_controller()
    assert ctrl.state == PlaybackState.STOPPED
    assert ctrl.current_frame == 0
    assert ctrl.position == 0.0


def test_play_transition(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.play()
    assert ctrl.state == PlaybackState.PLAYING
    ctrl.stop()


def test_play_idempotent(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.play()
    state = ctrl.state
    ctrl.play()
    assert ctrl.state == state
    ctrl.stop()


def test_pause_transition(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.play()
    ctrl.pause()
    assert ctrl.state == PlaybackState.PAUSED
    ctrl.stop()


def test_pause_when_stopped(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.pause()
    assert ctrl.state == PlaybackState.STOPPED


def test_stop_transition(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.play()
    ctrl.stop()
    assert ctrl.state == PlaybackState.STOPPED
    assert ctrl.current_frame == 0


def test_stop_when_stopped(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.stop()
    assert ctrl.state == PlaybackState.STOPPED


def test_seek(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.seek(50)
    assert ctrl.current_frame == 50
    assert ctrl.position == pytest.approx(50 / 99)


def test_seek_clamps_low(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.seek(-10)
    assert ctrl.current_frame == 0


def test_seek_clamps_high(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.seek(999)
    assert ctrl.current_frame == 99


def test_step_forward(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.seek(5)
    ctrl.step_forward()
    assert ctrl.current_frame == 6


def test_step_backward(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.seek(5)
    ctrl.step_backward()
    assert ctrl.current_frame == 4


def test_step_backward_at_start(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.step_backward()
    assert ctrl.current_frame == 0


def test_step_forward_at_end(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.seek(99)
    ctrl.step_forward()
    assert ctrl.current_frame == 99


def test_position_at_start(qapp):
    ctrl, _, _ = _make_controller()
    assert ctrl.position == 0.0


def test_position_at_end(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.seek(99)
    assert ctrl.position == 1.0


def test_position_single_frame(qapp):
    reader = MockReader()
    reader.total_frames = 1
    cache = FrameCache()
    ctrl = PlaybackController(reader, cache)
    assert ctrl.position == 0.0


def test_play_no_reader(qapp):
    reader = MockReader()
    reader.is_open = False
    reader.total_frames = 0
    cache = FrameCache()
    ctrl = PlaybackController(reader, cache)
    ctrl.play()
    assert ctrl.state == PlaybackState.STOPPED


def test_empty_reader(qapp):
    reader = MockReader()
    reader.total_frames = 0
    cache = FrameCache()
    ctrl = PlaybackController(reader, cache)
    ctrl.play()
    assert ctrl.state == PlaybackState.STOPPED


def test_set_speed(qapp):
    ctrl, _, _ = _make_controller()
    ctrl.set_speed(2.0)
    assert ctrl.state == PlaybackState.STOPPED
    ctrl.play()
    ctrl.set_speed(2.0)
    ctrl.stop()
    assert ctrl.state == PlaybackState.STOPPED


def test_seek_emits_signals(qapp):
    ctrl, _, _ = _make_controller()
    results = []
    ctrl.frame_changed.connect(lambda f: results.append(f))
    ctrl.position_changed.connect(lambda p: results.append(round(p, 4)))
    ctrl.seek(42)
    assert 42 in results
    assert 42 / 99 in results or round(42 / 99, 4) in results


def test_state_changed_signal_on_play(qapp):
    ctrl, _, _ = _make_controller()
    states = []
    ctrl.state_changed.connect(lambda s: states.append(s))
    ctrl.play()
    assert PlaybackState.PLAYING in states
    ctrl.stop()
