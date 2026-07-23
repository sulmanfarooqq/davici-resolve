import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
from core.undo_manager import UndoManager, GradeSnapshot


def _snapshot(**kw):
    return GradeSnapshot(**kw)


def test_init_state():
    um = UndoManager()
    assert len(um) == 0
    assert um.can_undo is False
    assert um.can_redo is False


def test_push_and_can_undo():
    um = UndoManager()
    um.push_state(_snapshot(grade_params={"sat": 0.5}))
    assert um.can_undo is True
    assert um.can_redo is False


def test_undo_returns_snapshot():
    um = UndoManager()
    s1 = _snapshot(grade_params={"sat": 0.5})
    s2 = _snapshot(grade_params={"sat": 0.8})
    um.push_state(s1)
    um.push_state(s2)
    result = um.undo()
    assert result is not None
    assert result.grade_params["sat"] == 0.5


def test_undo_then_redo():
    um = UndoManager()
    s1 = _snapshot(grade_params={"sat": 0.5})
    s2 = _snapshot(grade_params={"sat": 0.8})
    um.push_state(s1)
    um.push_state(s2)
    um.undo()
    result = um.redo()
    assert result is not None
    assert result.grade_params["sat"] == 0.8


def test_undo_empty_returns_none():
    um = UndoManager()
    assert um.undo() is None


def test_redo_empty_returns_none():
    um = UndoManager()
    um.push_state(_snapshot())
    um.undo()
    # redo should work (1 item undone)
    assert um.redo() is not None
    # redo again should return None
    assert um.redo() is None


def test_clear_resets_state():
    um = UndoManager()
    um.push_state(_snapshot(grade_params={"sat": 0.5}))
    um.clear()
    assert len(um) == 0
    assert um.can_undo is False
    assert um.can_redo is False


def test_max_stack_enforced():
    um = UndoManager(max_stack=3)
    for i in range(10):
        um.push_state(_snapshot(grade_params={"i": i}))
    assert len(um) <= 3
    # oldest entries are dropped
    um.undo()
    result = um.undo()
    # should still have the last item
    assert result is not None


def test_push_clears_redo():
    um = UndoManager()
    s1 = _snapshot(grade_params={"v": 1})
    s2 = _snapshot(grade_params={"v": 2})
    s3 = _snapshot(grade_params={"v": 3})
    um.push_state(s1)
    um.push_state(s2)
    um.undo()
    assert um.can_redo is True
    um.push_state(s3)
    assert um.can_redo is False
    assert um.undo().grade_params["v"] == 1


def test_undo_idempotent():
    um = UndoManager()
    assert um.undo() is None
    assert um.undo() is None
    assert um.can_undo is False


def test_redo_after_push():
    um = UndoManager()
    um.push_state(_snapshot(grade_params={"v": 1}))
    um.push_state(_snapshot(grade_params={"v": 2}))
    um.undo()
    assert um.can_redo is True
    # pushing a third snapshot should clear redo
    um.push_state(_snapshot(grade_params={"v": 3}))
    assert um.can_redo is False


def test_snapshot_with_node_graph():
    snap = GradeSnapshot(grade_params={"sat": 0.5}, node_graph={"nodes": [], "edges": []})
    assert snap.node_graph == {"nodes": [], "edges": []}
    assert snap.lut_path is None


def test_snapshot_with_lut():
    snap = GradeSnapshot(lut_path="/tmp/lut.cube")
    assert snap.lut_path == "/tmp/lut.cube"


def test_len_after_push():
    um = UndoManager()
    assert len(um) == 0
    um.push_state(_snapshot())
    assert len(um) == 1
    um.push_state(_snapshot())
    assert len(um) == 2
