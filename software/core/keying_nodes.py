"""Keying/matte nodes ported from Blender compositor nodes.
Sources:
  - source/blender/nodes/composite/nodes/node_composite_*.cc
  - source/blender/compositor/shaders/library/gpu_shader_compositor_*.glsl
"""

import numpy as np
from core.color_math import rgb_to_hsv, rgb_to_ycca_itu_709, ycca_to_rgba_itu_709, get_luminance


def node_color_key(image: np.ndarray, key_color: np.ndarray,
                   hue_threshold=0.1, sat_threshold=0.1, val_threshold=0.1) -> np.ndarray:
    hsv_img = rgb_to_hsv(image[..., :3])
    hsv_key = rgb_to_hsv(key_color[None, None, :3])
    dh = np.abs(hsv_img[..., 0] - hsv_key[..., 0])
    dh = np.minimum(dh, 1.0 - dh)
    ds = np.abs(hsv_img[..., 1] - hsv_key[..., 1])
    dv = np.abs(hsv_img[..., 2] - hsv_key[..., 2])
    matte = np.ones((image.shape[0], image.shape[1]), dtype=np.float32)
    inside = (dh <= hue_threshold) & (ds <= sat_threshold) & (dv <= val_threshold)
    matte[inside] = 0.0
    result = np.dstack([image[..., :3], matte])
    return result


def node_chroma_key(image: np.ndarray, key_color: np.ndarray,
                    angle_min=0.5, angle_max=1.0, falloff=0.1) -> np.ndarray:
    ycca = rgb_to_ycca_itu_709(image[..., :3])
    key_ycca = rgb_to_ycca_itu_709(key_color[None, None, :3])
    cb = ycca[..., 1]; cr = ycca[..., 2]
    kcb = key_ycca[..., 1]; kcr = key_ycca[..., 2]
    angle = np.abs(np.arctan2(cr - kcr, cb - kcb))
    matte = np.clip((angle - angle_min) / max(falloff, 1e-10), 0, 1)
    matte = np.where(angle < angle_min, 0.0, matte)
    matte = np.where(angle > angle_max, 1.0, matte)
    result = np.dstack([image[..., :3], matte])
    return result


def node_difference_key(image: np.ndarray, key_image: np.ndarray,
                        tolerance=0.1, falloff=0.1) -> np.ndarray:
    diff = np.abs(image[..., :3].astype(np.float32) - key_image[..., :3].astype(np.float32))
    avg_diff = diff.mean(axis=-1)
    matte = np.clip((avg_diff - tolerance) / max(falloff, 1e-10), 0, 1)
    result = np.dstack([image[..., :3], matte])
    return result


def node_luminance_key(image: np.ndarray, low=0.0, high=1.0) -> np.ndarray:
    luma = get_luminance(image[..., :3])
    matte = np.clip((luma - low) / max(high - low, 1e-10), 0, 1)
    result = np.dstack([image[..., :3], matte])
    return result


def node_channel_key(image: np.ndarray, color_space='RGB',
                     key_channel=0, limit_channel=0,
                     limit_method='single', min_val=0.0, max_val=1.0) -> np.ndarray:
    if color_space.upper() == 'HSV':
        conv = rgb_to_hsv(image[..., :3])
    elif color_space.upper() in ('YUV', 'YCC'):
        conv = rgb_to_ycca_itu_709(image[..., :3])
    else:
        conv = image[..., :3].astype(np.float32)
    key_val = conv[..., key_channel]
    if limit_method == 'single':
        limit_val = conv[..., limit_channel]
    else:
        others = [i for i in range(3) if i != key_channel]
        limit_val = conv[..., others].max(axis=-1)
    alpha = 1.0 - (key_val - limit_val)
    matte = np.clip((alpha - min_val) / max(max_val - min_val, 1e-10), 0, 1)
    result = np.dstack([image[..., :3], matte])
    return result


def node_distance_key(image: np.ndarray, key_color: np.ndarray,
                      tolerance=0.1, falloff=0.1, color_space='RGB') -> np.ndarray:
    if color_space.upper() == 'YCC':
        a = rgb_to_ycca_itu_709(image[..., :3])
        b = rgb_to_ycca_itu_709(key_color[None, None, :3])
    else:
        a = image[..., :3].astype(np.float32)
        b = key_color[None, None, :3].astype(np.float32)
    dist = np.sqrt(((a - b) ** 2).sum(axis=-1))
    matte = np.clip((dist - tolerance) / max(falloff, 1e-10), 0, 1)
    result = np.dstack([image[..., :3], matte])
    return result


def node_color_spill(image: np.ndarray, spill_channel=0, limit_method='single',
                     limit_channel=0, limit_strength=1.0, factor=1.0) -> np.ndarray:
    result = image.copy().astype(np.float32)
    if limit_method == 'single':
        limit_val = result[..., limit_channel]
    else:
        others = [i for i in range(3) if i != spill_channel]
        limit_val = result[..., others].mean(axis=-1)
    spill = result[..., spill_channel] - limit_val * limit_strength
    spill = np.maximum(spill * factor, 0)
    result[..., spill_channel] -= spill
    return np.clip(result, 0.0, 1.0)


def node_keying(image: np.ndarray, key_color: np.ndarray,
                blur_size=0, balance=0.5,
                black_level=0.0, white_level=1.0,
                despill_strength=0.5, despill_balance=0.5) -> np.ndarray:
    ycca = rgb_to_ycca_itu_709(image[..., :3])
    key_ycca = rgb_to_ycca_itu_709(key_color[None, None, :3])
    kcb = key_ycca[..., 1]; kcr = key_ycca[..., 2]
    cb = ycca[..., 1]; cr = ycca[..., 2]
    sat = np.sqrt(cb**2 + cr**2)
    key_sat = np.sqrt(kcb**2 + kcr**2)
    matte = 1.0 - np.clip((sat - balance * key_sat) / (key_sat + 1e-10), 0, 1)
    matte = np.clip((matte - black_level) / max(white_level - black_level, 1e-10), 0, 1)
    max_ch = np.argmax(key_color[:3])
    other_sum = sum(key_color[i] for i in range(3) if i != max_ch)
    spill_scale = despill_strength * key_color[max_ch] / max(other_sum, 1e-10)
    result = image.copy().astype(np.float32)
    result[..., max_ch] -= np.maximum(result[..., max_ch] - result[..., [i for i in range(3) if i != max_ch]].mean(axis=-1) * spill_scale, 0) * despill_balance
    if image.shape[-1] >= 4:
        result[..., 3] = matte
    else:
        result = np.dstack([result, matte[..., None]])
    return np.clip(result, 0.0, 1.0)
