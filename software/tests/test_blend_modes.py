import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import numpy as np
from core.blend_modes import *

def test_blend_mix():
    a = np.random.rand(10, 10, 3).astype(np.float32)
    b = np.random.rand(10, 10, 3).astype(np.float32)
    r = blend_mix(a, b, 0)
    assert np.allclose(r, a)
    r = blend_mix(a, b, 1)
    assert np.allclose(r, b)
    r = blend_mix(a, b, 0.5)
    assert np.allclose(r, (a + b) / 2)

def test_blend_add():
    a = np.full((1, 1, 3), 0.5)
    b = np.full((1, 1, 3), 0.3)
    r = blend_add(a, b, 1.0)
    assert np.allclose(r, 0.8)
    # Should clip
    r = blend_add(np.full((1, 1, 3), 0.8), np.full((1, 1, 3), 0.5), 1.0)
    assert np.allclose(r, 1.0)

def test_blend_subtract():
    a = np.full((1, 1, 3), 0.8)
    b = np.full((1, 1, 3), 0.3)
    r = blend_subtract(a, b, 1.0)
    assert np.allclose(r, 0.5)

def test_blend_multiply():
    a = np.full((1, 1, 3), 0.5)
    b = np.full((1, 1, 3), 0.8)
    r = blend_multiply(a, b, 0.0)
    assert np.allclose(r, a)
    r = blend_multiply(a, b, 1.0)
    assert np.allclose(r, a * b)

def test_blend_screen():
    a = np.full((1, 1, 3), 0.3)
    b = np.full((1, 1, 3), 0.4)
    r = blend_screen(a, b, 1.0)
    expected = 1 - (1 - a) * (1 - b)
    assert np.allclose(r, expected)

def test_blend_darken_lighten():
    a = np.array([[[0.3, 0.7, 0.5]]])
    b = np.array([[[0.6, 0.4, 0.5]]])
    r = blend_darken(a, b, 1.0)
    assert np.allclose(r, np.minimum(a, b))
    r = blend_lighten(a, b, 1.0)
    assert np.allclose(r, np.maximum(a, b))

def test_blend_difference():
    a = np.array([[[0.3, 0.7, 0.5]]])
    b = np.array([[[0.6, 0.4, 0.5]]])
    r = blend_difference(a, b, 1.0)
    assert np.allclose(r, np.abs(a - b))

def test_blend_divide():
    a = np.array([[[0.5, 0.5, 0.5]]])
    b = np.array([[[0.25, 0.5, 1.0]]])
    r = blend_divide(a, b, 1.0)
    assert np.allclose(r[0, 0, 0], 1.0, atol=1e-4)  # 0.5/0.25=2→clamp to 1
    assert np.allclose(r[0, 0, 1], 1.0, atol=1e-4)  # 0.5/0.5=1
    assert np.allclose(r[0, 0, 2], 0.5, atol=1e-4)  # 0.5/1.0=0.5

def test_blend_hard_soft_light():
    a = np.array([[[0.3, 0.6, 0.5]]])
    b = np.array([[[0.7, 0.4, 0.5]]])
    r_hard = blend_hard_light(a, b)
    r_overlay = blend_overlay(b, a)  # hard_light(x,y) = overlay(y,x)
    assert np.allclose(r_hard, r_overlay)

def test_blend_dodge_burn():
    a = np.array([[[0.5, 0.5, 0.5]]])
    b = np.array([[[0.5, 0.5, 0.5]]])
    r_dodge = blend_dodge(a, b, 1.0)
    r_burn = blend_burn(a, b, 1.0)
    assert np.all(r_dodge >= a[0, 0])
    assert np.all(r_burn <= a[0, 0])

def test_blend_exclusion():
    a = np.random.rand(10, 10, 3).astype(np.float32)
    b = np.random.rand(10, 10, 3).astype(np.float32)
    r = blend_exclusion(a, b, 1.0)
    assert r.shape == a.shape
    assert np.all((r >= 0) & (r <= 1))

def test_blend_linear_burn():
    a = np.full((1, 1, 3), 0.6)
    b = np.full((1, 1, 3), 0.5)
    r = blend_linear_burn(a, b, 1.0)
    assert np.allclose(r, 0.1)

def test_blend_all_modes():
    a = np.random.rand(5, 5, 3).astype(np.float32)
    b = np.random.rand(5, 5, 3).astype(np.float32)
    for name in BLEND_MODES:
        r = blend(name, a, b, 0.5)
        assert r.shape == a.shape, f"{name} shape mismatch"
        assert np.all((r >= 0) & (r <= 1)), f"{name} out of range"

def test_blend_unknown_mode():
    a = np.random.rand(5, 5, 3).astype(np.float32)
    b = np.random.rand(5, 5, 3).astype(np.float32)
    r = blend('unknown', a, b)
    assert np.allclose(r, blend_mix(a, b))

def test_blend_hsv_transfer():
    a = np.random.rand(5, 5, 3).astype(np.float32)
    b = np.random.rand(5, 5, 3).astype(np.float32)
    r = blend_hsv_transfer(a, b, 'h')
    assert r.shape == a.shape
    r = blend_hsv_transfer(a, b, 'hsv')
    assert r.shape == a.shape
