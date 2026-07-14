import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import numpy as np
from core.color_correction_nodes import *

def test_node_color_balance_lgg_identity():
    img = np.full((5, 5, 3), 0.18, dtype=np.float32)
    r = node_color_balance_lgg(img, lift=(1,1,1), gamma=(1,1,1), gain=(1,1,1))
    assert np.allclose(img, r, atol=1e-4)

def test_node_color_balance_lgg_factor():
    img = np.random.rand(5, 5, 3).astype(np.float32)
    r = node_color_balance_lgg(img, factor=0.0)
    assert np.allclose(r, img)
    r = node_color_balance_lgg(img, factor=0.5, gain=(1.5, 1.0, 1.0))
    assert r.shape == img.shape

def test_node_color_balance_cdl_identity():
    img = np.random.rand(5, 5, 3).astype(np.float32)
    r = node_color_balance_cdl(img)
    assert np.allclose(img, r, atol=1e-4)

def test_node_color_balance_cdl():
    img = np.full((1, 1, 3), 0.5)
    r = node_color_balance_cdl(img, slope=(2, 1, 1), offset=(0, 0, 0), power=(1, 1, 1))
    assert r[0, 0, 0] == 1.0

def test_node_brightness_contrast():
    img = np.random.rand(5, 5, 3).astype(np.float32)
    r = node_brightness_contrast(img, 0, 0)
    assert np.allclose(img, r)
    r = node_brightness_contrast(img, 50, 0)
    assert r.shape == img.shape

def test_node_exposure():
    img = np.full((1, 1, 3), 0.25)
    r = node_exposure(img, 1.0)
    assert abs(r[0, 0, 0] - 0.5) < 1e-6
    r = node_exposure(img, -1.0)
    assert abs(r[0, 0, 0] - 0.125) < 1e-6

def test_node_hue_saturation_value():
    img = np.random.rand(5, 5, 3).astype(np.float32)
    r = node_hue_saturation_value(img, 0, 0, 0)
    assert np.allclose(img, r, atol=1e-4)
    r = node_hue_saturation_value(img, 0.5, 0, 0)
    assert r.shape == img.shape

def test_node_gamma():
    img = np.random.rand(5, 5, 3).astype(np.float32)
    r = node_gamma(img, 1.0)
    assert np.allclose(img, r, atol=1e-4)
    r = node_gamma(img, 2.0)
    assert r.shape == img.shape

def test_node_invert():
    img = np.random.rand(5, 5, 3).astype(np.float32)
    r = node_invert(img, 1.0)
    assert np.allclose(r, 1.0 - img, atol=1e-4)
    r = node_invert(img, 0.0)
    assert np.allclose(r, img)

def test_node_invert_rgba():
    rgba = np.random.rand(5, 5, 4).astype(np.float32)
    r = node_invert(rgba, 1.0, invert_color=True, invert_alpha=True)
    assert np.allclose(r[..., :3], 1.0 - rgba[..., :3], atol=1e-6)
    assert np.allclose(r[..., 3], 1.0 - rgba[..., 3], atol=1e-6)

def test_node_posterize():
    img = np.random.rand(5, 5, 3).astype(np.float32)
    r = node_posterize(img, 16)
    assert r.shape == img.shape
    r = node_posterize(img, 2)
    assert np.allclose(r, np.floor(img * 2) / 2)

def test_node_color_correction_3way():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_color_correction_3way(img)
    assert r.shape == img.shape
    assert np.allclose(r, img, atol=1e-4)  # identity params

def test_node_color_correction_3way_params():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    shadows = {'saturation': 0.5, 'contrast': 0.0, 'gamma': 1.0, 'gain': 1.0, 'offset': 0.0}
    r = node_color_correction_3way(img, shadows=shadows)
    assert r.shape == img.shape
