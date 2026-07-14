import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import numpy as np
from core.color_space import *

def test_get_colorspace():
    cs = get_colorspace("srgb")
    assert cs is not None
    assert cs.name == "sRGB"
    assert get_colorspace("nonexistent") is None

def test_colorspace_identity():
    cs = get_colorspace("scene_linear")
    rgb = np.random.rand(5, 5, 3).astype(np.float32)
    result = cs.convert_to(rgb, cs)
    assert np.allclose(rgb, result)

def test_convert_srgb_to_linear():
    rgb = np.random.rand(5, 5, 3).astype(np.float32)
    result = convert_colorspace(rgb, "srgb", "scene_linear")
    assert result.shape == rgb.shape

def test_convert_roundtrip():
    rgb = np.random.rand(5, 5, 3).astype(np.float32)
    result = convert_colorspace(rgb, "rec709", "rec2020")
    back = convert_colorspace(result, "rec2020", "rec709")
    assert np.allclose(rgb, back, atol=1e-4)

def test_all_colorspace_conversions():
    names = list(COLOR_SPACES.keys())
    rgb = np.array([[[0.5, 0.3, 0.8]]], dtype=np.float32)
    for src in names:
        for dst in names:
            result = convert_colorspace(rgb, src, dst)
            assert result.shape == rgb.shape

def test_srgb_transfer_forward():
    linear = np.array([0.0, 0.0031308, 0.5, 1.0])
    encoded = srgb_transfer_forward(linear)
    assert encoded[0] == 0.0
    assert np.allclose(encoded[3], 1.0)
    assert np.all(encoded >= 0)

def test_srgb_transfer_inverse():
    encoded = np.array([0.0, 0.04045, 0.5, 1.0])
    linear = srgb_transfer_inverse(encoded)
    assert linear[0] == 0.0
    assert linear[3] == 1.0

def test_srgb_transfer_roundtrip():
    linear = np.random.rand(10, 10, 3).astype(np.float32)
    encoded = srgb_transfer_forward(linear)
    back = srgb_transfer_inverse(encoded)
    assert np.allclose(linear, back, atol=1e-4)

def test_luma_coefficients():
    assert np.allclose(LUMA_BT709, [0.2126, 0.7152, 0.0722])
    assert np.allclose(LUMA_BT2020, [0.2627, 0.6780, 0.0593])

def test_colorspace_to_dict():
    cs = get_colorspace("srgb")
    assert cs is not None
