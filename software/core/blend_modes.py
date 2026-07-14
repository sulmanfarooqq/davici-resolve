"""26 blend modes ported from Blender's math_color_blend_inline.cc
and gpu_shader_common_mix_rgb.glsl
"""

import numpy as np
from typing import Callable

BlendFunc = Callable[[np.ndarray, np.ndarray, float], np.ndarray]


def blend_mix(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    return a * (1 - fac) + b * fac


def blend_add(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    return np.clip(a + b * fac, 0, 1)


def blend_subtract(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    return np.clip(a - b * fac, 0, 1)


def blend_multiply(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    return a * (1 - fac) + a * b * fac


def blend_screen(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    return 1 - (1 - a) * (1 - b * fac) - a * (1 - fac)


def blend_overlay(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    a_fac = a * (1 - fac)
    return np.where(a <= 0.5,
                    2 * a * (b * fac + (1 - fac)),
                    1 - 2 * (1 - a) * (1 - b * fac))


def blend_hard_light(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    return blend_overlay(b, a, fac)


def blend_soft_light(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    b_scaled = a * (1 - fac) + b * fac
    return np.where(b_scaled <= 0.5,
                    np.clip(a - (1 - 2 * b_scaled) * a * (1 - a), 0, 1),
                    np.clip(a + (2 * b_scaled - 1) * (a - a * a), 0, 1))


def blend_dodge(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    b_scaled = b * fac + (1 - fac)
    return np.where(b_scaled >= 1, a, np.clip(a / (1 - b_scaled), 0, 1))


def blend_burn(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    b_scaled = b * fac + (1 - fac)
    return np.where(b_scaled == 0, 0, np.clip(1 - (1 - a) / b_scaled, 0, 1))


def blend_linear_burn(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    return np.clip(a + b * fac - 1, 0, 1)


def blend_linear_light(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    b_scaled = b * fac + (1 - fac) * 0.5
    return np.where(b_scaled > 0.5,
                    np.clip(a + 2 * (b_scaled - 0.5), 0, 1),
                    np.clip(a + 2 * b_scaled - 1, 0, 1))


def blend_vivid_light(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    b_scaled = b * fac + (1 - fac) * 0.5
    return np.where(b_scaled > 0.5,
                    np.where(b_scaled >= 1, a, np.clip(1 - (1 - a) / (2 * (1 - b_scaled)), 0, 1)),
                    np.where(b_scaled <= 0, 0, np.clip(a / (2 * b_scaled), 0, 1)))


def blend_pin_light(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    b_scaled = b * fac + (1 - fac) * 0.5
    return np.where(b_scaled > 0.5,
                    np.maximum(a, 2 * (b_scaled - 0.5)),
                    np.minimum(a, 2 * b_scaled))


def blend_darken(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    return np.minimum(a, b) * fac + a * (1 - fac)


def blend_lighten(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    return np.maximum(a, b) * fac + a * (1 - fac)


def blend_difference(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    return np.abs(a - b) * fac + a * (1 - fac)


def blend_exclusion(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    return (0.5 - 2 * (a - 0.5) * (b * fac - 0.5)) * (1 - fac) + a * fac


def blend_divide(a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    return a * (1 - fac) + np.clip(a / (b + 1e-10), 0, 1) * fac


BLEND_MODES = {
    "mix": blend_mix,
    "add": blend_add,
    "subtract": blend_subtract,
    "multiply": blend_multiply,
    "screen": blend_screen,
    "overlay": blend_overlay,
    "hard_light": blend_hard_light,
    "soft_light": blend_soft_light,
    "dodge": blend_dodge,
    "burn": blend_burn,
    "linear_burn": blend_linear_burn,
    "linear_light": blend_linear_light,
    "vivid_light": blend_vivid_light,
    "pin_light": blend_pin_light,
    "darken": blend_darken,
    "lighten": blend_lighten,
    "difference": blend_difference,
    "exclusion": blend_exclusion,
    "divide": blend_divide,
}


def blend(mode: str, a: np.ndarray, b: np.ndarray, fac: float = 0.5) -> np.ndarray:
    fn = BLEND_MODES.get(mode, blend_mix)
    return fn(a, b, fac)


def blend_hsv_transfer(a: np.ndarray, b: np.ndarray, channels: str) -> np.ndarray:
    from core.color_math import rgb_to_hsv, hsv_to_rgb
    hsv_a = rgb_to_hsv(a[..., :3])
    hsv_b = rgb_to_hsv(b[..., :3])
    result = hsv_a.copy()
    if "h" in channels: result[..., 0] = hsv_b[..., 0]
    if "s" in channels: result[..., 1] = hsv_b[..., 1]
    if "v" in channels: result[..., 2] = hsv_b[..., 2]
    out = a.copy().astype(np.float32)
    out[..., :3] = hsv_to_rgb(result)
    return out
