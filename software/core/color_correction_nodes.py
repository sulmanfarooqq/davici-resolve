"""Color correction nodes — each is a function: image -> params -> image.
Ported from Blender compositor nodes.
"""

import numpy as np
from core.color_math import (
    colorbalance_cdl, colorbalance_lgg, linearrgb_to_srgb, srgb_to_linearrgb,
    get_luminance, apply_brightness_contrast, apply_exposure, apply_saturation,
    apply_gamma, apply_invert, apply_posterize, rgb_to_hsv, hsv_to_rgb
)


def node_color_balance_lgg(image: np.ndarray, lift=(0.,0.,0.), gamma=(1.,1.,1.),
                           gain=(1.,1.,1.), offset=(0.,0.,0.), factor=1.0) -> np.ndarray:
    result = image.copy().astype(np.float32)
    for c in range(3):
        l = lift[c]; g = 1.0 / max(gamma[c], 0.001); gn = gain[c]
        result[:,:,c] = colorbalance_lgg(result[:,:,c], l, g, gn)
    result[:,:,:3] += np.array(offset)
    if factor < 1.0:
        result = image * (1 - factor) + result * factor
    return np.clip(result, 0.0, 1.0)


def node_color_balance_cdl(image: np.ndarray, slope=(1.,1.,1.), offset=(0.,0.,0.),
                           power=(1.,1.,1.), factor=1.0) -> np.ndarray:
    result = image.copy().astype(np.float32)
    for c in range(3):
        result[:,:,c] = colorbalance_cdl(result[:,:,c],
                                          np.array([slope[c]]),
                                          np.array([offset[c]]),
                                          np.array([1.0 / max(power[c], 0.001)]))
    if factor < 1.0:
        result = image * (1 - factor) + result * factor
    return np.clip(result, 0.0, 1.0)


def node_brightness_contrast(image: np.ndarray, brightness=0.0, contrast=0.0) -> np.ndarray:
    return apply_brightness_contrast(image, brightness, contrast)


def node_exposure(image: np.ndarray, exposure=0.0) -> np.ndarray:
    return apply_exposure(image, exposure)


def node_hue_saturation_value(image: np.ndarray, hue=0.0, saturation=0.0,
                              value=0.0, factor=1.0) -> np.ndarray:
    hsv = rgb_to_hsv(image[..., :3])
    hsv[..., 0] = (hsv[..., 0] + hue) % 1.0
    hsv[..., 1] = np.clip(hsv[..., 1] * (1.0 + saturation), 0, 1)
    hsv[..., 2] = np.clip(hsv[..., 2] * (1.0 + value), 0, 1)
    result = image.copy().astype(np.float32)
    result[..., :3] = hsv_to_rgb(hsv)
    if factor < 1.0:
        result = image * (1 - factor) + result * factor
    return result


def node_gamma(image: np.ndarray, gamma=1.0) -> np.ndarray:
    return apply_gamma(image, gamma)


def node_invert(image: np.ndarray, factor=1.0, invert_color=True, invert_alpha=False) -> np.ndarray:
    return apply_invert(image, factor, invert_color, invert_alpha)


def node_posterize(image: np.ndarray, steps=32) -> np.ndarray:
    result = image.copy().astype(np.float32)
    result[..., :3] = apply_posterize(image, steps)
    return result


def node_color_correction_3way(image: np.ndarray,
                                shadows: dict = None,
                                midtones: dict = None,
                                highlights: dict = None,
                                midtones_start=0.2, midtones_end=0.8) -> np.ndarray:
    if shadows is None: shadows = {'saturation': 1.0, 'contrast': 0.0, 'gamma': 1.0, 'gain': 1.0, 'offset': 0.0}
    if midtones is None: midtones = {'saturation': 1.0, 'contrast': 0.0, 'gamma': 1.0, 'gain': 1.0, 'offset': 0.0}
    if highlights is None: highlights = {'saturation': 1.0, 'contrast': 0.0, 'gamma': 1.0, 'gain': 1.0, 'offset': 0.0}

    luma = get_luminance(image)
    margin = 0.1

    def range_weight(l, start, end):
        return np.clip((l - start + margin) / (2 * margin), 0, 1) * \
               np.clip((end - l + margin) / (2 * margin), 0, 1)

    w_shadow = 1.0 - np.clip((luma - midtones_start + margin) / (2 * margin), 0, 1)
    w_highlight = np.clip((luma - midtones_end + margin) / (2 * margin), 0, 1)
    w_midtone = 1.0 - w_shadow - w_highlight

    def apply_region(img, params):
        s = params.get('saturation', 1.0)
        c = params.get('contrast', 0.0)
        g = params.get('gamma', 1.0)
        gn = params.get('gain', 1.0)
        o = params.get('offset', 0.0)
        result = img.copy().astype(np.float32)
        l = get_luminance(result)
        for i in range(3):
            result[..., i] = l + (result[..., i] - l) * s
        result = (result - 0.5) * (1 + c) + 0.5
        result = np.clip(result, 0.0, 1.0)
        result[..., :3] = np.power(result[..., :3], 1.0 / max(g, 0.001)) * gn + o
        return result

    s_result = apply_region(image, shadows)
    m_result = apply_region(image, midtones)
    h_result = apply_region(image, highlights)

    result = image.copy().astype(np.float32)
    for i in range(3):
        result[..., i] = (s_result[..., i] * w_shadow +
                          m_result[..., i] * w_midtone +
                          h_result[..., i] * w_highlight)
    return np.clip(result, 0.0, 1.0)
