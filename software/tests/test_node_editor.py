import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import pytest
pyside6 = pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication
from core.node_graph import NodeGraph
from nodes import NODE_CLASSES
from ui.widgets.node_editor import NodeEditor


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def graph():
    return NodeGraph()


@pytest.fixture
def editor(qapp, graph):
    return NodeEditor(graph, NODE_CLASSES)


def test_editor_init(qapp, editor):
    assert editor.graph is not None
    assert editor.node_classes is NODE_CLASSES


def test_editor_rebuild(qapp, editor):
    editor.rebuild()
    assert editor._scene is not None
    assert editor._view is not None


def test_editor_reset(qapp, editor):
    graph = editor.graph
    from nodes import ExposureNode
    graph.add_node(ExposureNode("test1"))
    graph.add_node(ExposureNode("test2"))
    assert len(graph.nodes) == 2
    editor._reset()
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0


def test_graph_changed_signal_on_reset(qapp, editor):
    signals = []
    editor.graph_changed.connect(lambda: signals.append(1))
    editor._reset()
    assert len(signals) >= 1


def test_node_classes_available(qapp, editor):
    assert "exposure" in editor.node_classes
    assert "color_balance_cdl" in editor.node_classes
    assert "rgb_curves" in editor.node_classes
    assert "keying" in editor.node_classes


def test_node_graph_from_dict_with_classes(qapp, graph):
    from nodes import create_node
    graph.add_node(create_node("exposure", "exp1"))
    graph.add_node(create_node("gamma", "gam1"))
    graph.connect(list(graph.nodes.keys())[0], "Image",
                  list(graph.nodes.keys())[1], "Image")
    data = graph.to_dict()
    restored = NodeGraph.from_dict(data, NODE_CLASSES)
    assert len(restored.nodes) == 2
    assert len(restored.edges) == 1
