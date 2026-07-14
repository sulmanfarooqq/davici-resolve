import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import numpy as np
from nodes import create_node, NODE_CLASSES
from core.node_graph import NodeGraph


def test_all_node_types_exist():
    assert len(NODE_CLASSES) >= 15
    expected = ["color_balance_lgg", "color_balance_cdl", "brightness_contrast",
                "exposure", "hue_saturation_value", "gamma", "invert", "posterize",
                "rgb_curves", "hue_correct", "tonemap", "alpha_over", "levels",
                "keying", "color_spill", "blend", "pixelate"]
    for name in expected:
        assert name in NODE_CLASSES, f"Missing node: {name}"

def test_create_each_node():
    for name, cls in NODE_CLASSES.items():
        node = create_node(name)
        assert node.type == name
        assert len(node.outputs) >= 1

def test_node_process_without_inputs():
    for name in NODE_CLASSES:
        node = create_node(name)
        result = node.process({})
        assert isinstance(result, np.ndarray), f"{name} didn't return array"

def test_node_blend_graph():
    g = NodeGraph()
    a = create_node("brightness_contrast")
    b = create_node("gamma")
    a.params = {'brightness': 20, 'contrast': 10}
    b.params = {'gamma': 1.2}
    # Wire: nothing→a→b
    g.add_node(a); g.add_node(b)
    g.connect(a.id, "Image", b.id, "Image")
    result = g.execute()
    assert result is not None
    assert isinstance(result, np.ndarray)

def test_node_invert_graph():
    g = NodeGraph()
    inv = create_node("invert")
    g.add_node(inv)
    inv.params = {'factor': 0.5}
    result = g.execute()
    assert result is not None

def test_node_graph_multi_chain():
    g = NodeGraph()
    bc = create_node("brightness_contrast")
    exp = create_node("exposure")
    g.add_node(bc); g.add_node(exp)
    g.connect(bc.id, "Image", exp.id, "Image")
    result = g.execute()
    assert result is not None

def test_create_node_unknown():
    import traceback
    try:
        create_node("nonexistent")
        assert False, "Should raise ValueError"
    except ValueError:
        pass
