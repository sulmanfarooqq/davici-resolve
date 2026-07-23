"""Color math ported from Blender's GPL compositor source.

Sources:
  - source/blender/blenlib/BLI_math_color_c.hh
  - source/blender/blenlib/intern/math_color.cc
  - source/blender/blenlib/intern/math_color_inline.cc
  - source/blender/compositor/shaders/library/gpu_shader_common_color_utils.glsl
  - source/blender/compositor/shaders/library/gpu_shader_compositor_color_balance.glsl
"""

import numpy as np
from typing import Tuple, Optional

# ─── sRGB / Linear ───

def linearrgb_to_srgb(c: np.ndarray) -> np.ndarray:
    mask = c <= 0.0031308
    return np.where(mask, c * 12.92, 1.055 * np.power(np.maximum(c, 0.0), 1.0 / 2.4) - 0.055)

def srgb_to_linearrgb(c: np.ndarray) -> np.ndarray:
    mask = c <= 0.04045
    return np.where(mask, c / 12.92, np.power((np.maximum(c, 0.0) + 0.055) / 1.055, 2.4))

def srgb_to_linearrgb_uchar4(c: np.ndarray) -> np.ndarray:
    return srgb_to_linearrgb(c.astype(np.float32) / 255.0)

def linearrgb_to_srgb_uchar4(c: np.ndarray) -> np.ndarray:
    return np.clip(linearrgb_to_srgb(c) * 255.0, 0, 255).astype(np.uint8)

# ─── Luminance (Rec.709) ───

LUMA_COEFFS_709 = np.array([0.2126, 0.7152, 0.0722])

def get_luminance(rgb: np.ndarray) -> np.ndarray:
    return rgb[..., 0] * LUMA_COEFFS_709[0] + rgb[..., 1] * LUMA_COEFFS_709[1] + rgb[..., 2] * LUMA_COEFFS_709[2]

# ─── RGB ↔ HSV ───

def rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn
    h = np.where(mx == mn, 0.0,
                 np.where(mx == r, np.mod((g - b) / (d + 1e-10), 6.0),
                 np.where(mx == g, (b - r) / (d + 1e-10) + 2.0,
                                    (r - g) / (d + 1e-10) + 4.0))) * 60.0 / 360.0
    s = np.divide(d, mx, out=np.zeros_like(d), where=mx > 0)
    v = mx
    return np.stack([h, s, v], axis=-1)

def hsv_to_rgb(hsv: np.ndarray) -> np.ndarray:
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    h = h * 6.0
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    r = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
                  [v, q, p, p, t, v])
    g = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
                  [t, v, v, q, p, p])
    b = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
                  [p, p, t, v, v, q])
    return np.stack([r, g, b], axis=-1)

# ─── RGB ↔ HSL ───

def rgb_to_hsl(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    l = (mx + mn) / 2.0
    d = mx - mn
    h = np.where(mx == mn, 0.0,
                 np.where(mx == r, np.mod((g - b) / (d + 1e-10), 6.0),
                 np.where(mx == g, (b - r) / (d + 1e-10) + 2.0,
                                    (r - g) / (d + 1e-10) + 4.0))) * 60.0 / 360.0
    s = np.where(d == 0, 0.0, np.where(l > 0.5, d / (2.0 - mx - mn + 1e-10), d / (mx + mn + 1e-10)))
    return np.stack([h, s, l], axis=-1)

def hsl_to_rgb(hsl: np.ndarray) -> np.ndarray:
    h, s, l = hsl[..., 0], hsl[..., 1], hsl[..., 2]
    c = (1.0 - np.abs(2.0 * l - 1.0)) * s
    x = c * (1.0 - np.abs(np.mod(h * 6.0, 2.0) - 1.0))
    m = l - c / 2.0
    i = np.floor(h * 6.0).astype(int) % 6
    r = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
                  [c, x, 0, 0, x, c])
    g = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
                  [x, c, c, x, 0, 0])
    b = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
                  [0, 0, x, c, c, x])
    return np.stack([r + m, g + m, b + m], axis=-1)

# ─── YUV / YCbCr (ITU-R standards) ───

def rgb_to_yuv_itu_709(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    u = -0.0999 * r - 0.3360 * g + 0.4360 * b
    v = 0.6150 * r - 0.5586 * g - 0.0564 * b
    return np.stack([y, u, v], axis=-1)

def yuv_to_rgb_itu_709(yuv: np.ndarray) -> np.ndarray:
    y, u, v = yuv[..., 0], yuv[..., 1], yuv[..., 2]
    r = y + 1.2803 * v
    g = y - 0.2148 * u - 0.3805 * v
    b = y + 2.1279 * u
    return np.stack([r, g, b], axis=-1)

def rgb_to_yuv_itu_601(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    u = -0.147 * r - 0.289 * g + 0.436 * b
    v = 0.615 * r - 0.515 * g - 0.100 * b
    return np.stack([y, u, v], axis=-1)

def yuv_to_rgb_itu_601(yuv: np.ndarray) -> np.ndarray:
    y, u, v = yuv[..., 0], yuv[..., 1], yuv[..., 2]
    r = y + 1.140 * v
    g = y - 0.394 * u - 0.581 * v
    b = y + 2.032 * u
    return np.stack([r, g, b], axis=-1)

def rgb_to_ycca_itu_709(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    cb = -0.0999 * r - 0.3360 * g + 0.4360 * b
    cr = 0.6150 * r - 0.5586 * g - 0.0564 * b
    return np.stack([y, cb, cr], axis=-1)

def ycca_to_rgba_itu_709(ycca: np.ndarray) -> np.ndarray:
    y, cb, cr = ycca[..., 0], ycca[..., 1], ycca[..., 2]
    r = y + 1.2803 * cr
    g = y - 0.2148 * cb - 0.3805 * cr
    b = y + 2.1279 * cb
    return np.stack([r, g, b], axis=-1)

def rgb_to_ycca_itu_601(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = -0.168736 * r - 0.331264 * g + 0.5 * b
    cr = 0.5 * r - 0.418688 * g - 0.081312 * b
    return np.stack([y, cb, cr], axis=-1)

def ycca_to_rgba_itu_601(ycca: np.ndarray) -> np.ndarray:
    y, cb, cr = ycca[..., 0], ycca[..., 1], ycca[..., 2]
    r = y + 1.402 * cr
    g = y - 0.344136 * cb - 0.714136 * cr
    b = y + 1.772 * cb
    return np.stack([r, g, b], axis=-1)

def rgb_to_ycca_jpeg(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = -0.168736 * r - 0.331264 * g + 0.5 * b + 0.5
    cr = 0.5 * r - 0.418688 * g - 0.081312 * b + 0.5
    return np.stack([y, cb, cr], axis=-1)

def ycca_to_rgba_jpeg(ycca: np.ndarray) -> np.ndarray:
    y, cb, cr = ycca[..., 0], ycca[..., 1], ycca[..., 2]
    cb = cb - 0.5; cr = cr - 0.5
    r = y + 1.402 * cr
    g = y - 0.344136 * cb - 0.714136 * cr
    b = y + 1.772 * cb
    return np.stack([r, g, b], axis=-1)

# ─── Alpha handling ───

def straight_to_premul(rgba: np.ndarray) -> np.ndarray:
    result = rgba.copy()
    result[..., :3] *= rgba[..., 3:4]
    return result

def premul_to_straight(rgba: np.ndarray) -> np.ndarray:
    result = rgba.copy()
    mask = rgba[..., 3] > 1e-8
    result[..., 0] = np.where(mask, rgba[..., 0] / rgba[..., 3], 0)
    result[..., 1] = np.where(mask, rgba[..., 1] / rgba[..., 3], 0)
    result[..., 2] = np.where(mask, rgba[..., 2] / rgba[..., 3], 0)
    return result

# ─── ASC CDL (Slope/Offset/Power) — Blender's colorbalance_cdl ───

def colorbalance_cdl(in_val: np.ndarray, slope: np.ndarray, offset: np.ndarray, power: np.ndarray) -> np.ndarray:
    x = in_val * slope + offset
    x = np.clip(x, 0.0, 1.0)
    return np.power(x, power)

# ─── Lift/Gamma/Gain — Blender's colorbalance_lgg ───

def colorbalance_lgg(in_val: np.ndarray, lift: np.ndarray, gamma_inv: np.ndarray, gain: np.ndarray) -> np.ndarray:
    x = ((linearrgb_to_srgb(in_val) - 1.0) * (2.0 - lift) + 1.0) * gain
    x = np.maximum(x, 0.0)
    return srgb_to_linearrgb(np.power(x, gamma_inv))


def colorbalance_lgg_rgb(image: np.ndarray, lift_rgb, gamma_inv_rgb, gain_rgb) -> np.ndarray:
    if image.ndim == 2:
        return colorbalance_lgg(image, lift_rgb, gamma_inv_rgb, gain_rgb)
    x = ((linearrgb_to_srgb(image[..., :3]) - 1.0) * (2.0 - np.asarray([lift_rgb])) + 1.0) * np.asarray([gain_rgb])
    x = np.maximum(x, 0.0)
    return srgb_to_linearrgb(np.power(x, np.asarray([gamma_inv_rgb])))

# ─── White Point / Temperature / Tint (Blender Bradford adaptation) ───

def whitepoint_from_temp_tint(temperature: float, tint: float) -> np.ndarray:
    if temperature <= 0:
        return np.array([1.0, 1.0, 1.0])
    temp = np.clip(temperature, 1667, 25000)
    if temp <= 4000:
        x = -0.2661239 * (1e9 / temp**3) - 0.2343580 * (1e6 / temp**2) + 0.8776956 * (1e3 / temp) + 0.179910
    else:
        x = -3.0258469 * (1e9 / temp**3) + 2.1070379 * (1e6 / temp**2) + 0.2226347 * (1e3 / temp) + 0.240390
    y = -3.0 * x**2 + 2.87 * x - 0.275
    Y = 1.0
    X = x / y * Y
    Z = (1.0 - x - y) / y * Y
    white = np.array([X, Y, Z])
    tint_offset = np.array([tint * 0.01, 0.0, tint * -0.01])
    return white + tint_offset

BRADFORD = np.array([
    [0.8951, 0.2664, -0.1614],
    [-0.7502, 1.7135, 0.0367],
    [0.0389, -0.0685, 1.0296]
])
BRADFORD_INV = np.linalg.inv(BRADFORD)

def chromatic_adaption_matrix(from_XYZ: np.ndarray, to_XYZ: np.ndarray) -> np.ndarray:
    from_lms = BRADFORD @ from_XYZ
    to_lms = BRADFORD @ to_XYZ
    scale = np.diag(to_lms / (from_lms + 1e-10))
    return BRADFORD_INV @ scale @ BRADFORD

# ─── Brightness/Contrast (Werner D. Streidt, from OpenCV) ───

def apply_brightness_contrast(image: np.ndarray, brightness: float = 0.0, contrast: float = 0.0) -> np.ndarray:
    b = brightness / 100.0
    delta = contrast / 200.0
    if contrast > 0:
        mul = 1.0 / max(1.0 - delta * 2, 1e-10)
        add = mul * (b - delta)
    else:
        mul = max(1.0 - delta * 2, 0.0)
        add = mul * b + delta
    return np.clip(image * mul + add, 0.0, 1.0)

# ─── Exposure ───

def apply_exposure(image: np.ndarray, exposure: float = 0.0) -> np.ndarray:
    return image * np.float32(2.0 ** exposure)

# ─── Saturation ───

def apply_saturation(image: np.ndarray, saturation: float = 0.0) -> np.ndarray:
    luma = get_luminance(image)
    factor = 1.0 + saturation
    result = luma[..., None] + (image[..., :3] - luma[..., None]) * factor
    return np.clip(result, 0.0, 1.0)

# ─── Gamma ───

def apply_gamma(image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
    return np.power(np.maximum(image, 0.0), 1.0 / max(gamma, 0.001))

# ─── Invert ───

def apply_invert(image: np.ndarray, factor: float = 1.0, invert_color: bool = True, invert_alpha: bool = False) -> np.ndarray:
    result = image.copy().astype(np.float32)
    if invert_color and image.shape[-1] >= 3:
        result[..., :3] = (1.0 - image[..., :3]) * factor + image[..., :3] * (1.0 - factor)
    if invert_alpha and image.shape[-1] >= 4:
        result[..., 3] = (1.0 - image[..., 3]) * factor + image[..., 3] * (1.0 - factor)
    return result

# ─── Posterize ───

def apply_posterize(image: np.ndarray, steps: int = 32) -> np.ndarray:
    steps = np.clip(steps, 2, 1024)
    return np.floor(image[..., :3] * steps) / steps

# ─── Map Range ───

def map_range_linear(value: np.ndarray, from_min: float = 0.0, from_max: float = 1.0,
                     to_min: float = 0.0, to_max: float = 1.0, clamp: bool = False) -> np.ndarray:
    factor = (value - from_min) / (from_max - from_min + 1e-10)
    if clamp:
        factor = np.clip(factor, 0.0, 1.0)
    return to_min + factor * (to_max - to_min)

def map_range_smoothstep(value: np.ndarray, from_min: float = 0.0, from_max: float = 1.0,
                         to_min: float = 0.0, to_max: float = 1.0) -> np.ndarray:
    t = np.clip((value - from_min) / (from_max - from_min + 1e-10), 0.0, 1.0)
    t = t * t * (3.0 - 2.0 * t)
    return to_min + t * (to_max - to_min)

# ─── Normalize ───

def apply_normalize(image: np.ndarray) -> np.ndarray:
    mn = image.min(axis=(0, 1), keepdims=True)
    mx = image.max(axis=(0, 1), keepdims=True)
    rng = mx - mn
    rng = np.where(rng < 1e-10, 1.0, rng)
    return (image - mn) / rng


# ─── Performance: LUT-based grading ───

LGG_LUT_SIZE = 4096
_LGG_LUT_X = np.linspace(0, 1, LGG_LUT_SIZE, dtype=np.float64)


def make_lgg_lut_channel(lift: float, gamma_inv: float, gain: float) -> np.ndarray:
    y = ((linearrgb_to_srgb(_LGG_LUT_X) - 1.0) * (2.0 - lift) + 1.0) * gain
    y = np.maximum(y, 0.0)
    y = srgb_to_linearrgb(np.power(y, gamma_inv))
    return np.clip(y, 0, 1).astype(np.float32)


def apply_lut_1d(channel: np.ndarray, lut: np.ndarray) -> None:
    idx = np.clip(channel * (len(lut) - 1) + 0.5, 0, len(lut) - 1).astype(np.int32)
    channel[:] = lut[idx]


def apply_lut_1d_fast(channel: np.ndarray, lut: np.ndarray) -> np.ndarray:
    return lut[np.clip(channel * (len(lut) - 1) + 0.5, 0, len(lut) - 1).astype(np.int32)]


class GradingCache:
    """Caches LGG LUTs. Only rebuilds when parameters actually change."""

    def __init__(self):
        self._lut_r = None
        self._lut_g = None
        self._lut_b = None
        self._lift = (None, None, None)
        self._gamma_inv = (None, None, None)
        self._gain = (None, None, None)

    def _needs_rebuild(self, lift, gamma_inv, gain) -> bool:
        return (
            self._lut_r is None
            or lift != self._lift
            or gamma_inv != self._gamma_inv
            or gain != self._gain
        )

    def get_luts(self, lift_rgb, gamma_inv_rgb, gain_rgb):
        if self._needs_rebuild(lift_rgb, gamma_inv_rgb, gain_rgb):
            self._lut_r = make_lgg_lut_channel(lift_rgb[0], gamma_inv_rgb[0], gain_rgb[0])
            self._lut_g = make_lgg_lut_channel(lift_rgb[1], gamma_inv_rgb[1], gain_rgb[1])
            self._lut_b = make_lgg_lut_channel(lift_rgb[2], gamma_inv_rgb[2], gain_rgb[2])
            self._lift = tuple(lift_rgb)
            self._gamma_inv = tuple(gamma_inv_rgb)
            self._gain = tuple(gain_rgb)
        return self._lut_r, self._lut_g, self._lut_b

    def apply_lgg(self, image: np.ndarray, lift_rgb, gamma_inv_rgb, gain_rgb) -> np.ndarray:
        lut_r, lut_g, lut_b = self.get_luts(lift_rgb, gamma_inv_rgb, gain_rgb)
        result = image.copy()
        result[..., 0] = apply_lut_1d_fast(result[..., 0], lut_r)
        result[..., 1] = apply_lut_1d_fast(result[..., 1], lut_g)
        result[..., 2] = apply_lut_1d_fast(result[..., 2], lut_b)
        return result

    def apply_lgg_inplace(self, image: np.ndarray, lift_rgb, gamma_inv_rgb, gain_rgb) -> None:
        lut_r, lut_g, lut_b = self.get_luts(lift_rgb, gamma_inv_rgb, gain_rgb)
        apply_lut_1d(image[..., 0], lut_r)
        apply_lut_1d(image[..., 1], lut_g)
        apply_lut_1d(image[..., 2], lut_b)
