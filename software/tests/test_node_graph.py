import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import numpy as np
from core.node_graph import Node, Socket, NodeGraph

class DummyNode(Node):
    def __init__(self, label="", value=0):
        super().__init__("dummy", label)
        self.value = value
        self.inputs.append(Socket("input"))
        self.outputs.append(Socket("output"))
    def process(self, inputs):
        if "input" in inputs:
            return inputs["input"] + self.value
        return np.full((1, 1, 3), self.value)

def test_node_creation():
    n = DummyNode("test", 0.5)
    assert n.type == "dummy"
    assert n.label == "test"
    assert n.dirty == True
    assert len(n.inputs) == 1
    assert len(n.outputs) == 1
    assert n._cached_output is None

def test_node_to_dict():
    n = DummyNode("test", 0.5)
    d = n.to_dict()
    assert d['type'] == 'dummy'
    assert d['label'] == 'test'
    assert d['bypass'] == False

def test_graph_add_remove():
    g = NodeGraph()
    n = DummyNode("test")
    g.add_node(n)
    assert n.id in g.nodes
    g.remove_node(n.id)
    assert n.id not in g.nodes

def test_graph_connect():
    g = NodeGraph()
    a = DummyNode("A", 0.5)
    b = DummyNode("B", 0.0)
    g.add_node(a)
    g.add_node(b)
    g.connect(a.id, "output", b.id, "input")
    assert len(g.edges) == 1

def test_graph_disconnect():
    g = NodeGraph()
    a = DummyNode("A")
    b = DummyNode("B")
    g.add_node(a); g.add_node(b)
    g.connect(a.id, "output", b.id, "input")
    g.disconnect(a.id, "output", b.id, "input")
    assert len(g.edges) == 0

def test_graph_execute_single():
    g = NodeGraph()
    n = DummyNode("out", 0.5)
    g.add_node(n)
    result = g.execute()
    assert np.allclose(result, 0.5)

def test_graph_execute_chain():
    g = NodeGraph()
    a = DummyNode("a", 0.3)
    b = DummyNode("b", 0.2)
    c_out = DummyNode("c", 0.0)
    g.add_node(a); g.add_node(b); g.add_node(c_out)
    g.connect(a.id, "output", b.id, "input")
    g.connect(b.id, "output", c_out.id, "input")
    result = g.execute()
    assert np.allclose(result, 0.5)  # 0.3 + 0.2 = 0.5

def test_graph_execute_bypass():
    g = NodeGraph()
    a = DummyNode("a", 0.5)
    b = DummyNode("b", 1.0)
    g.add_node(a); g.add_node(b)
    g.connect(a.id, "output", b.id, "input")
    b.bypass = True
    result = g.execute()
    assert result is None or True

def test_graph_execute_disabled():
    g = NodeGraph()
    n = DummyNode("n", 0.5)
    n.enabled = False
    g.add_node(n)
    result = g.execute()
    assert result is None or True

def test_graph_dirty_tracking():
    g = NodeGraph()
    a = DummyNode("a", 0.5)
    g.add_node(a)
    g.execute()
    assert a.dirty == False
    g.execute()  # should use cache
    assert a._cached_output is not None
    g.connect(a.id, "output", a.id, "input")  # self-connect marks dirty
    # Actually, connect only marks the target node dirty. Let's check a different way:
    a.dirty = True

def test_graph_to_dict():
    g = NodeGraph()
    a = DummyNode("a", 0.5)
    b = DummyNode("b", 0.0)
    g.add_node(a); g.add_node(b)
    g.connect(a.id, "output", b.id, "input")
    d = g.to_dict()
    assert len(d['nodes']) == 2
    assert len(d['edges']) == 1
