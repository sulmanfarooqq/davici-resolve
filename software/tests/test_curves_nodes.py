import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import numpy as np
from core.curves_nodes import *

def test_evaluate_curve_empty():
    x = np.array([0.0, 0.5, 1.0])
    r = evaluate_curve([], x)
    assert np.allclose(r, x)

def test_evaluate_curve_identity():
    pts = [(0, 0), (1, 1)]
    x = np.random.rand(100).astype(np.float32)
    r = evaluate_curve(pts, x)
    assert np.allclose(r, x, atol=1e-4)

def test_evaluate_curve_linear():
    pts = [(0, 0), (1, 1)]
    x = np.linspace(0, 1, 100)
    r = evaluate_curve(pts, x)
    assert np.allclose(r, x, atol=1e-4)

def test_evaluate_curve_single_point():
    pts = [(0.5, 0.3)]
    x = np.array([0.0, 0.5, 1.0])
    r = evaluate_curve(pts, x)
    assert np.allclose(r, 0.3)

def test_evaluate_curve_inverted():
    pts = [(0, 1), (1, 0)]
    x = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    r = evaluate_curve(pts, x)
    assert r[0] > r[-1]  # decreasing

def test_evaluate_curve_lut_size():
    pts = [(0, 0), (1, 1)]
    x = np.linspace(0, 1, 1000)
    r = evaluate_curve(pts, x)
    assert r.shape == x.shape

def test_node_rgb_curves_identity():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_rgb_curves(img, factor=1.0)
    assert np.allclose(img, r, atol=1e-4)

def test_node_rgb_curves_invert():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    curves = {'RGB': [(0, 1), (1, 0)]}
    r = node_rgb_curves(img, curves=curves)
    assert np.allclose(r, 1.0 - img, atol=1e-3)

def test_node_rgb_curves_factor():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_rgb_curves(img, factor=0.0)
    assert np.allclose(r, img)

def test_node_rgb_curves_black_white():
    img = np.array([[[0.2, 0.5, 0.8]]])
    curves = {'RGB': [(0,0),(1,1)]}
    r = node_rgb_curves(img, curves=curves, black_level=(0.1, 0.1, 0.1), white_level=(0.9, 0.9, 0.9))
    assert r.shape == img.shape

def test_node_rgb_curves_per_channel():
    img = np.array([[[0.25, 0.5, 0.75]]])
    curves = {'R': [(0,0),(1,1)], 'G': [(0,0),(1,1)], 'B': [(0,0),(1,1)]}
    r = node_rgb_curves(img, curves=curves)
    assert np.allclose(img, r, atol=1e-4)

def test_node_hue_correct_identity():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    curves = {'H': [(0,0.5),(1,0.5)], 'S': [(0,0.5),(1,0.5)], 'V': [(0,0.5),(1,0.5)]}
    r = node_hue_correct(img, curves=curves)
    assert np.allclose(img, r, atol=1e-4)

def test_node_hue_correct_factor():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_hue_correct(img, factor=0.0)
    assert np.allclose(r, img)

def test_node_hue_correct_hue_shift():
    img = np.array([[[0.8, 0.2, 0.2]]])  # reddish
    curves = {'H': [(0,0.5),(1,0.5)]}  # no shift
    r1 = node_hue_correct(img, curves=curves)
    curves2 = {'H': [(0,1.0),(1,1.0)]}  # max shift
    r2 = node_hue_correct(img, curves=curves2)
    assert not np.allclose(r1, r2)  # should differ

def test_node_float_curve_identity():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_float_curve(img, [(0,0),(1,1)])
    assert np.allclose(img, r, atol=1e-4)

def test_node_float_curve_invert():
    img = np.random.rand(10, 10).astype(np.float32)
    r = node_float_curve(img, [(0,1),(1,0)])
    assert np.allclose(r, 1 - img, atol=1e-3)

def test_node_float_curve_factor():
    img = np.random.rand(10, 10).astype(np.float32)
    r = node_float_curve(img, factor=0.0)
    assert np.allclose(r, img)
    r = node_float_curve(img, factor=1.0)
    assert r.shape == img.shape
