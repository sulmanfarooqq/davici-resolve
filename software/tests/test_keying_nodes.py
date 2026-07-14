import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import numpy as np
from core.keying_nodes import *

def test_node_color_key():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    key = np.array([0.0, 1.0, 0.0])
    r = node_color_key(img, key, 0.1, 0.1, 0.1)
    assert r.shape == (10, 10, 4)
    assert np.all((r[..., 3] >= 0) & (r[..., 3] <= 1))

def test_node_chroma_key():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    key = np.array([0.0, 1.0, 0.0])
    r = node_chroma_key(img, key)
    assert r.shape == (10, 10, 4)

def test_node_difference_key():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    key = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_difference_key(img, key)
    assert r.shape == (10, 10, 4)

def test_node_luminance_key():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_luminance_key(img, 0.2, 0.8)
    assert r.shape == (10, 10, 4)

def test_node_channel_key():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_channel_key(img, 'RGB', 0, 1)
    assert r.shape == (10, 10, 4)

def test_node_channel_key_hsv():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_channel_key(img, 'HSV', 0, 1)
    assert r.shape == (10, 10, 4)

def test_node_channel_key_ycc():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_channel_key(img, 'YCC', 0, 1)
    assert r.shape == (10, 10, 4)

def test_node_distance_key():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    key = np.array([0.0, 1.0, 0.0])
    r = node_distance_key(img, key)
    assert r.shape == (10, 10, 4)

def test_node_distance_key_ycc():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    key = np.array([0.0, 1.0, 0.0])
    r = node_distance_key(img, key, color_space='YCC')
    assert r.shape == (10, 10, 4)

def test_node_color_spill():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_color_spill(img, 0, 'single', 1)
    assert r.shape == img.shape

def test_node_keying():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    key = np.array([0.0, 1.0, 0.0])
    r = node_keying(img, key)
    assert r.shape == (10, 10, 4)
