import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import numpy as np
from core.color_math import *

# ─── sRGB / Linear ───

def test_linearrgb_to_srgb():
    c = np.array([0.0, 0.0031308, 0.5, 1.0])
    r = linearrgb_to_srgb(c)
    assert r[0] == 0.0
    assert abs(r[1] - 0.0031308 * 12.92) < 1e-6
    assert np.allclose(r[3], 1.0)
    assert np.all(r >= 0) and np.all(r <= 1)

def test_srgb_to_linearrgb():
    c = np.array([0.0, 0.04045, 0.5, 1.0])
    r = srgb_to_linearrgb(c)
    assert r[0] == 0.0
    assert r[3] == 1.0

def test_srgb_roundtrip():
    c = np.random.rand(100, 100, 3).astype(np.float32)
    r = srgb_to_linearrgb(linearrgb_to_srgb(c))
    assert np.allclose(c, r, atol=1e-4)

def test_srgb_uchar4():
    c = np.array([[127, 200, 50, 255]], dtype=np.uint8)
    r = srgb_to_linearrgb_uchar4(c)
    assert r.shape == (1, 4)
    assert np.all(r >= 0) and np.all(r <= 1)
    back = linearrgb_to_srgb_uchar4(r)
    assert np.allclose(back, c, atol=1)

# ─── Luminance ───

def test_get_luminance():
    rgb = np.array([[[0.2126, 0.7152, 0.0722]]])
    l = get_luminance(rgb)
    assert abs(l[0, 0] - 0.2126*0.2126 - 0.7152*0.7152 - 0.0722*0.0722) < 1e-6

def test_get_luminance_black():
    assert get_luminance(np.zeros((1, 1, 3))) == 0.0

def test_get_luminance_white():
    assert abs(get_luminance(np.ones((1, 1, 3))) - 1.0) < 1e-6

# ─── RGB ↔ HSV ───

def test_rgb_to_hsv_identity():
    rgb = np.random.rand(10, 10, 3).astype(np.float32)
    hsv = rgb_to_hsv(rgb)
    back = hsv_to_rgb(hsv)
    assert np.allclose(rgb, back, atol=1e-6)

def test_rgb_to_hsv_black():
    hsv = rgb_to_hsv(np.zeros((1, 1, 3)))
    assert hsv[0, 0, 2] == 0.0  # v=0

def test_rgb_to_hsv_white():
    hsv = rgb_to_hsv(np.ones((1, 1, 3)))
    assert hsv[0, 0, 1] == 0.0  # s=0
    assert hsv[0, 0, 2] == 1.0  # v=1

def test_rgb_to_hsv_red():
    hsv = rgb_to_hsv(np.array([[[1.0, 0.0, 0.0]]]))
    assert abs(hsv[0, 0, 0]) < 1e-6  # h=0
    assert hsv[0, 0, 1] == 1.0
    assert hsv[0, 0, 2] == 1.0

# ─── RGB ↔ HSL ───

def test_rgb_to_hsl_roundtrip():
    rgb = np.random.rand(10, 10, 3).astype(np.float32)
    hsl = rgb_to_hsl(rgb)
    back = hsl_to_rgb(hsl)
    assert np.allclose(rgb, back, atol=1e-6)

def test_rgb_to_hsl_gray():
    for v in [0.0, 0.5, 1.0]:
        hsl = rgb_to_hsl(np.full((1, 1, 3), v))
        assert hsl[0, 0, 1] == 0.0  # s=0 for gray

# ─── YUV / YCbCr ───

def test_yuv_709_roundtrip():
    rgb = np.random.rand(5, 5, 3).astype(np.float32)
    yuv = rgb_to_yuv_itu_709(rgb)
    back = yuv_to_rgb_itu_709(yuv)
    assert np.allclose(rgb, back, atol=1e-3)

def test_yuv_601_roundtrip():
    rgb = np.random.rand(5, 5, 3).astype(np.float32)
    yuv = rgb_to_yuv_itu_601(rgb)
    back = yuv_to_rgb_itu_601(yuv)
    assert np.allclose(rgb, back, atol=1e-3)

def test_ycca_709_roundtrip():
    rgb = np.random.rand(5, 5, 3).astype(np.float32)
    ycca = rgb_to_ycca_itu_709(rgb)
    back = ycca_to_rgba_itu_709(ycca)
    assert np.allclose(rgb, back, atol=1e-3)

def test_ycca_601_roundtrip():
    rgb = np.random.rand(5, 5, 3).astype(np.float32)
    ycca = rgb_to_ycca_itu_601(rgb)
    back = ycca_to_rgba_itu_601(ycca)
    assert np.allclose(rgb, back, atol=1e-6)

def test_ycca_jpeg_roundtrip():
    rgb = np.random.rand(5, 5, 3).astype(np.float32)
    ycca = rgb_to_ycca_jpeg(rgb)
    back = ycca_to_rgba_jpeg(ycca)
    assert np.allclose(rgb, back, atol=1e-6)

# ─── Alpha handling ───

def test_straight_to_premul():
    rgba = np.array([[[0.5, 0.5, 0.5, 0.5]]])
    p = straight_to_premul(rgba)
    assert np.allclose(p[0, 0, :3], [0.25, 0.25, 0.25])
    assert p[0, 0, 3] == 0.5

def test_premul_to_straight():
    rgba = np.array([[[0.25, 0.25, 0.25, 0.5]]])
    s = premul_to_straight(rgba)
    assert np.allclose(s[0, 0, :3], [0.5, 0.5, 0.5])
    assert s[0, 0, 3] == 0.5

def test_alpha_roundtrip():
    rgba = np.random.rand(5, 5, 4).astype(np.float32)
    rgba[..., 3] = np.random.rand(5, 5)  # random alpha
    p = straight_to_premul(rgba)
    s = premul_to_straight(p)
    assert np.allclose(rgba, s, atol=1e-6)

# ─── ASC CDL ───

def test_colorbalance_cdl_identity():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    result = colorbalance_cdl(img, np.ones(3), np.zeros(3), np.ones(3))
    assert np.allclose(img, result, atol=1e-6)

def test_colorbalance_cdl_slope():
    img = np.full((1, 1, 3), 0.5)
    result = colorbalance_cdl(img, np.array([2.0, 1.0, 1.0]), np.zeros(3), np.ones(3))
    assert result[0, 0, 0] == 1.0  # 0.5*2=1.0
    assert abs(result[0, 0, 1] - 0.5) < 1e-6

def test_colorbalance_cdl_offset():
    img = np.zeros((1, 1, 3))
    result = colorbalance_cdl(img, np.ones(3), np.array([0.5, 0.0, 0.0]), np.ones(3))
    assert result[0, 0, 0] == 0.5

# ─── LGG ───

def test_colorbalance_lgg_identity():
    img = np.full((1, 1, 3), 0.18)
    result = colorbalance_lgg(img, np.ones(3), np.ones(3), np.ones(3))
    assert np.allclose(img, result, atol=1e-4)

# ─── White point ───

def test_whitepoint_from_temp_tint():
    wp = whitepoint_from_temp_tint(6500, 0)
    assert wp.shape == (3,)
    assert np.all(wp > 0)

def test_whitepoint_tint():
    wp = whitepoint_from_temp_tint(6500, 10)
    assert wp[0] > wp[2]  # tint offsets X positive, Z negative

# ─── Brightness / Contrast ───

def test_brightness_contrast_identity():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    result = apply_brightness_contrast(img, 0, 0)
    assert np.allclose(img, result, atol=1e-6)

def test_brightness_positive():
    img = np.zeros((1, 1, 3))
    result = apply_brightness_contrast(img, 50, 0)
    assert result[0, 0, 0] > 0

def test_contrast_positive():
    img = np.full((1, 1, 3), 0.25)
    result = apply_brightness_contrast(img, 0, 50)
    assert result[0, 0, 0] < 0.25  # below mid-gray gets darker with increased contrast

# ─── Exposure ───

def test_exposure_identity():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    assert np.allclose(apply_exposure(img, 0), img)

def test_exposure_stop():
    img = np.full((1, 1, 3), 0.25)
    result = apply_exposure(img, 1)
    assert abs(result[0, 0, 0] - 0.5) < 1e-6  # 0.25 * 2^1 = 0.5

def test_exposure_negative():
    img = np.full((1, 1, 3), 0.5)
    result = apply_exposure(img, -1)
    assert abs(result[0, 0, 0] - 0.25) < 1e-6

# ─── Saturation ───

def test_saturation_identity():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    assert np.allclose(apply_saturation(img, 0), img, atol=1e-6)

def test_saturation_zero():
    img = np.array([[[0.8, 0.2, 0.2]]])
    result = apply_saturation(img, -1.0)
    l = get_luminance(img)
    assert np.allclose(result, l, atol=1e-6)

# ─── Gamma ───

def test_gamma_identity():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    assert np.allclose(apply_gamma(img, 1.0), img, atol=1e-6)

def test_gamma_half():
    img = np.full((1, 1, 3), 0.25)
    result = apply_gamma(img, 2.0)
    assert abs(result[0, 0, 0] - 0.5) < 1e-6

# ─── Invert ───

def test_invert_full():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    result = apply_invert(img, 1.0, True, False)
    assert np.allclose(result[..., :3], 1.0 - img[..., :3], atol=1e-6)

def test_invert_alpha():
    rgba = np.random.rand(10, 10, 4).astype(np.float32)
    result = apply_invert(rgba, 1.0, True, True)
    assert np.allclose(result[..., :3], 1.0 - rgba[..., :3], atol=1e-6)
    assert np.allclose(result[..., 3], 1.0 - rgba[..., 3], atol=1e-6)

# ─── Posterize ───

def test_posterize():
    img = np.array([[[0.25, 0.5, 0.75]]])
    result = apply_posterize(img, 4)
    assert result[0, 0, 0] == 0.25  # floor(0.25*4)/4 = 1/4 = 0.25
    assert result[0, 0, 1] == 0.5   # floor(0.5*4)/4 = 2/4 = 0.5
    assert result[0, 0, 2] == 0.75  # floor(0.75*4)/4 = 3/4 = 0.75

def test_posterize_one_step():
    img = np.random.rand(10, 10, 3).astype(np.float32)
    result = apply_posterize(img, 2)
    assert np.all((result == 0) | (result == 0.5))

# ─── Map Range ───

def test_map_range_linear():
    v = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    r = map_range_linear(v, 0, 1, 0, 255)
    assert np.allclose(r, v * 255)
    r2 = map_range_linear(np.array([-0.5, 1.5]), 0, 1, 0, 1, clamp=True)
    assert r2[0] == 0 and r2[1] == 1

def test_map_range_smoothstep():
    r = map_range_smoothstep(np.array([0.0, 0.5, 1.0]), 0, 1, 0, 1)
    assert r[0] == 0 and r[2] == 1
    assert 0 < r[1] < 0.5  # smoothstep eases in

# ─── Normalize ───

def test_apply_normalize():
    img = np.array([[[0.0, 0.0, 0.0], [0.5, 1.0, 0.25]]])
    r = apply_normalize(img)
    assert r[0, 0, 0] == 0.0 and r[0, 0, 0] == 0.0
    assert np.allclose(r[0, 1, 0], 1.0)  # 0.5 normalized to max
    assert r[0, 1, 1] == 1.0

def test_apply_normalize_constant():
    img = np.ones((5, 5, 3))
    r = apply_normalize(img)
    assert np.allclose(r, 0.0)  # constant → (img-mn)/rng = 0/1 = 0
