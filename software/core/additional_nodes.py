"""Additional compositor nodes.
Sources:
  - source/blender/nodes/composite/nodes/node_composite_tonemap.cc
  - source/blender/nodes/composite/nodes/node_composite_alpha_over.cc
  - source/blender/nodes/composite/nodes/node_composite_levels.cc
  - source/blender/nodes/composite/nodes/node_composite_combine_color.cc
  - source/blender/nodes/composite/nodes/node_composite_separate_color.cc
  - source/blender/nodes/composite/nodes/node_composite_glare.cc
"""

import numpy as np
from core.color_math import srgb_to_linearrgb, linearrgb_to_srgb, get_luminance


# ─── ToneMap (Reinhard + Photoreceptor) ───

def node_tonemap_reinhard(image: np.ndarray, key: float = 0.18, offset: float = 0.0,
                          gamma: float = 1.0) -> np.ndarray:
    luminance = get_luminance(image[..., :3])
    scaled_lum = luminance * key
    toned_lum = scaled_lum / (scaled_lum + 1.0 + offset)
    scale = toned_lum / (luminance + 1e-10)
    result = image.copy().astype(np.float32)
    result[..., :3] = result[..., :3] * scale[..., None]
    if gamma != 1.0:
        result[..., :3] = np.power(np.maximum(result[..., :3], 0.0), 1.0 / max(gamma, 0.001))
    return np.clip(result, 0.0, 1.0)


def node_tonemap_photoreceptor(image: np.ndarray, intensity: float = 0.0,
                               contrast: float = 0.0, adaptation: float = 1.0,
                               gamma: float = 1.0) -> np.ndarray:
    lin = srgb_to_linearrgb(image[..., :3])
    log_lum = np.log(np.maximum(get_luminance(lin), 1e-10))
    log_avg = np.mean(log_lum)
    log_adapt = log_avg * adaptation
    lum_adapt = np.exp(log_adapt)
    lum_d = lin.astype(np.float32).copy()
    for i in range(3):
        lum_d[..., i] /= (lum_d[..., i] + lum_adapt)
    lum_d = np.power(np.maximum(lum_d * (1.0 + intensity), 0.0), max(contrast + 1.0, 0.001))
    result = image.copy().astype(np.float32)
    result[..., :3] = linearrgb_to_srgb(lum_d)
    if gamma != 1.0:
        result[..., :3] = np.power(np.maximum(result[..., :3], 0.0), 1.0 / max(gamma, 0.001))
    return np.clip(result, 0.0, 1.0)


# ─── Alpha Over ───

def node_alpha_over(image: np.ndarray, overlay: np.ndarray,
                    premul: bool = True, factor: float = 1.0) -> np.ndarray:
    img = image.copy().astype(np.float32)
    ov = overlay.copy().astype(np.float32)
    if img.shape[-1] == 3:
        img = np.dstack([img, np.ones_like(img[..., 0])])
    if ov.shape[-1] == 3:
        ov = np.dstack([ov, np.ones_like(ov[..., 0])])
    if not premul:
        ov[..., :3] *= ov[..., 3:4]
        img[..., :3] *= img[..., 3:4]
    a = ov[..., 3:4] * factor
    out_a = a + img[..., 3:4] * (1.0 - a)
    out_rgb = (ov[..., :3] * a + img[..., :3] * (1.0 - a)) / (out_a + 1e-10)
    result = np.dstack([out_rgb, out_a[..., 0]])
    if not premul:
        result[..., :3] *= result[..., 3:4]
    return np.clip(result, 0.0, 1.0)


def node_alpha_set(image: np.ndarray, alpha: np.ndarray = None, value: float = 1.0) -> np.ndarray:
    result = image.copy().astype(np.float32)
    if alpha is not None:
        result[..., 3] = alpha
    else:
        result[..., 3] = value
    return np.clip(result, 0.0, 1.0)


# ─── Levels ───

def node_levels(image: np.ndarray, channel: int = 0,
                in_min: float = 0.0, in_max: float = 1.0,
                out_min: float = 0.0, out_max: float = 1.0,
                gamma: float = 1.0) -> np.ndarray:
    result = image.copy().astype(np.float32)
    if channel == 0:
        ch_data = get_luminance(result[..., :3])
    else:
        ch_data = result[..., channel - 1].copy()
    ch_data = (ch_data - in_min) / max(in_max - in_min, 1e-10)
    ch_data = np.clip(ch_data, 0.0, 1.0)
    ch_data = np.power(ch_data, gamma)
    ch_data = out_min + ch_data * (out_max - out_min)
    if channel == 0:
        luma = get_luminance(result[..., :3])
        for i in range(3):
            scaled = result[..., i] * ch_data
            result[..., i] = np.divide(scaled, luma, out=np.zeros_like(scaled), where=luma > 1e-10)
    else:
        result[..., channel - 1] = ch_data
    return np.clip(result, 0.0, 1.0)


# ─── Combine / Separate Color ───

def node_combine_color(r: np.ndarray, g: np.ndarray, b: np.ndarray,
                       mode: str = 'RGB') -> np.ndarray:
    if mode == 'HSV':
        from core.color_math import hsv_to_rgb
        hsv = np.stack([r, g, b], axis=-1)
        return hsv_to_rgb(hsv)
    elif mode == 'HSL':
        from core.color_math import hsl_to_rgb
        hsl = np.stack([r, g, b], axis=-1)
        return hsl_to_rgb(hsl)
    elif mode in ('YUV', 'YCC'):
        from core.color_math import yuv_to_rgb_itu_601
        yuv = np.stack([r, g, b], axis=-1)
        return yuv_to_rgb_itu_601(yuv)
    return np.clip(np.stack([r, g, b], axis=-1), 0.0, 1.0)


def node_separate_color(image: np.ndarray, mode: str = 'RGB') -> np.ndarray:
    if mode == 'HSV':
        from core.color_math import rgb_to_hsv
        return rgb_to_hsv(image[..., :3])
    elif mode == 'HSL':
        from core.color_math import rgb_to_hsl
        return rgb_to_hsl(image[..., :3])
    elif mode in ('YUV', 'YCC'):
        from core.color_math import rgb_to_yuv_itu_601
        return rgb_to_yuv_itu_601(image[..., :3])
    return image[..., :3].copy()


# ─── Convert Colorspace ───

def node_convert_colorspace(image: np.ndarray, from_cs: str = 'srgb',
                            to_cs: str = 'scene_linear') -> np.ndarray:
    from core.color_space import convert_colorspace
    return convert_colorspace(image, from_cs, to_cs)


# ─── Pixelate (Mosaic) ───

def node_pixelate(image: np.ndarray, size: int = 10) -> np.ndarray:
    h, w = image.shape[:2]
    size = max(1, size)
    result = image.copy()
    for y in range(0, h, size):
        for x in range(0, w, size):
            block = result[y:min(y+size, h), x:min(x+size, w)]
            avg = block.mean(axis=(0, 1), keepdims=True)
            result[y:min(y+size, h), x:min(x+size, w)] = avg
    return result
