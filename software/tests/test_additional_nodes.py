import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import numpy as np
from core.additional_nodes import *

def test_tonemap_reinhard_identity():
    img = np.full((5, 5, 3), 0.18, dtype=np.float32)
    r = node_tonemap_reinhard(img, key=0.18)
    assert r.shape == img.shape
    assert np.all((r >= 0) & (r <= 1))

def test_tonemap_reinhard_highlights():
    img = np.full((5, 5, 3), 10.0, dtype=np.float32)
    r = node_tonemap_reinhard(img, key=0.18)
    assert r.shape == img.shape
    assert np.all(r <= 1.0)

def test_tonemap_photoreceptor():
    img = np.full((5, 5, 3), 0.5, dtype=np.float32)
    r = node_tonemap_photoreceptor(img)
    assert r.shape == img.shape
    assert np.all((r >= 0) & (r <= 1))

def test_alpha_over_basic():
    bg = np.full((10, 10, 4), [0.0, 0.0, 0.0, 1.0], dtype=np.float32)
    fg = np.full((10, 10, 4), [1.0, 0.0, 0.0, 0.5], dtype=np.float32)
    r = node_alpha_over(bg, fg)
    assert r.shape == (10, 10, 4)
    assert r[0, 0, 0] > 0 and r[0, 0, 0] < 1.0

def test_alpha_over_rgb_input():
    bg = np.full((10, 10, 3), 0.0, dtype=np.float32)
    fg = np.full((10, 10, 3), 1.0, dtype=np.float32)
    r = node_alpha_over(bg, fg)
    assert r.shape == (10, 10, 4)

def test_alpha_set_value():
    img = np.full((10, 10, 4), [0.5, 0.5, 0.5, 0.0], dtype=np.float32)
    r = node_alpha_set(img, value=0.8)
    assert np.allclose(r[..., 3], 0.8)

def test_alpha_set_array():
    img = np.full((10, 10, 4), [0.5, 0.5, 0.5, 0.0], dtype=np.float32)
    alpha = np.full((10, 10), 0.3)
    r = node_alpha_set(img, alpha=alpha)
    assert np.allclose(r[..., 3], 0.3)

def test_levels_luminance():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_levels(img, channel=0, in_min=0.2, in_max=0.8)
    assert r.shape == img.shape

def test_levels_per_channel():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    for ch in [1, 2, 3]:
        r = node_levels(img, channel=ch, gamma=0.5)
        assert r.shape == img.shape

def test_combine_color_rgb():
    r = node_combine_color(np.full((5,5), 0.5), np.full((5,5), 0.3), np.full((5,5), 0.7))
    assert r.shape == (5, 5, 3)

def test_combine_color_hsv():
    r = node_combine_color(np.full((5,5), 0.5), np.full((5,5), 0.3), np.full((5,5), 0.7), 'HSV')
    assert r.shape == (5, 5, 3)

def test_combine_color_hsl():
    r = node_combine_color(np.full((5,5), 0.5), np.full((5,5), 0.3), np.full((5,5), 0.7), 'HSL')
    assert r.shape == (5, 5, 3)

def test_separate_color_rgb():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_separate_color(img, 'RGB')
    assert r.shape == (10, 10, 3)

def test_separate_color_hsv():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_separate_color(img, 'HSV')
    assert r.shape == (10, 10, 3)

def test_convert_colorspace():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    r = node_convert_colorspace(img, 'srgb', 'scene_linear')
    assert r.shape == img.shape

def test_pixelate():
    img = np.random.rand(20, 20, 3).astype(np.float32)
    r = node_pixelate(img, 5)
    assert r.shape == img.shape
    # Check that blocks are uniform
    assert np.allclose(r[0:5, 0:5], r[0, 0], atol=1e-6)
