"""Additional compositor nodes.
Sources:
  - source/blender/nodes/composite/nodes/node_composite_tonemap.cc
  - source/blender/nodes/composite/nodes/node_composite_alpha_over.cc
  - source/blender/nodes/composite/nodes/node_composite_levels.cc
  - source/blender/nodes/composite/nodes/node_composite_combine_color.cc
  - source/blender/nodes/composite/nodes/node_composite_separate_color.cc
  - source/blender/nodes/composite/nodes/node_composite_glare.cc
  - source/blender/nodes/composite/nodes/node_composite_blur.cc
  - source/blender/nodes/composite/nodes/node_composite_filter.cc
"""

import numpy as np
from core.color_math import (
    srgb_to_linearrgb, linearrgb_to_srgb, get_luminance,
    rgb_to_hsv, hsv_to_rgb, whitepoint_from_temp_tint,
    chromatic_adaption_matrix,
)


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


# ─── Shadows / Highlights ───

def node_shadows_highlights(image: np.ndarray, shadows: float = 0.0, highlights: float = 0.0,
                            shadow_tone: float = 0.5, highlight_tone: float = 0.5,
                            color_correction: float = 0.0) -> np.ndarray:
    """Adjust shadows and highlights independently. Ported from Blender compositor.
    shadows/highlights: -1..1 strength, shadow_tone/highlight_tone: 0..1 tonal range."""
    luma = get_luminance(image[..., :3])
    shadow_mask = np.clip(1.0 - luma / max(shadow_tone, 0.01), 0, 1)
    highlight_mask = np.clip((luma - (1.0 - highlight_tone)) / max(highlight_tone, 0.01), 0, 1)
    result = image.copy().astype(np.float32)
    if shadows != 0.0:
        for c in range(min(3, result.shape[-1])):
            result[..., c] += shadows * shadow_mask
    if highlights != 0.0:
        for c in range(min(3, result.shape[-1])):
            result[..., c] += highlights * highlight_mask
    if color_correction != 0.0:
        hsv = rgb_to_hsv(np.clip(result[..., :3], 0, 1))
        hsv[..., 1] = np.clip(hsv[..., 1] * (1.0 + color_correction * shadow_mask), 0, 1)
        result[..., :3] = hsv_to_rgb(hsv)
    return np.clip(result, 0.0, 1.0)


# ─── Color Temperature ───

def node_color_temperature(image: np.ndarray, temperature: float = 6500.0,
                           tint: float = 0.0) -> np.ndarray:
    """White balance by color temperature (Kelvin) + tint. Uses Bradford chromatic adaptation."""
    white = whitepoint_from_temp_tint(temperature, tint)
    d65 = np.array([1.0, 1.0, 1.0])
    M = chromatic_adaption_matrix(white, d65)
    lin = srgb_to_linearrgb(image[..., :3].astype(np.float32))
    flat = lin.reshape(-1, 3)
    adapted = (M @ flat.T).T
    adapted = adapted.reshape(lin.shape)
    result = image.copy().astype(np.float32)
    result[..., :3] = linearrgb_to_srgb(np.clip(adapted, 0, 1))
    return np.clip(result, 0.0, 1.0)


# ─── Split Toning ───

def node_split_toning(image: np.ndarray, shadow_color: tuple = (0.5, 0.5, 0.6),
                      highlight_color: tuple = (0.6, 0.5, 0.4),
                      balance: float = 0.0, factor: float = 1.0) -> np.ndarray:
    """Apply separate color tints to shadows and highlights."""
    luma = get_luminance(image[..., :3])
    shadow_t = np.clip(1.0 - luma * 2.0, 0, 1)
    highlight_t = np.clip(luma * 2.0 - 1.0, 0, 1)
    sc = np.array(shadow_color[:3])
    hc = np.array(highlight_color[:3])
    result = image.copy().astype(np.float32)
    for c in range(min(3, result.shape[-1])):
        tint_val = sc[c] * shadow_t + hc[c] * highlight_t
        result[..., c] += (tint_val - 0.5) * 0.3 * factor
    if balance != 0.0:
        result[..., :3] *= 1.0 + balance * 0.1
    return np.clip(result, 0.0, 1.0)


# ─── Vignette ───

def node_vignette(image: np.ndarray, strength: float = 0.5, size: float = 0.8,
                  feather: float = 0.4, center_x: float = 0.5,
                  center_y: float = 0.5) -> np.ndarray:
    """Apply radial vignette darkening/lightening."""
    h, w = image.shape[:2]
    y_coords, x_coords = np.mgrid[0:h, 0:w].astype(np.float32)
    cx = center_x * w
    cy = center_y * h
    max_r = max(w, h) * 0.5
    dx = (x_coords - cx) / max_r
    dy = (y_coords - cy) / max_r
    dist = np.sqrt(dx * dx + dy * dy)
    inner = size * 0.5
    outer = inner + feather * 0.5
    vignette_mask = np.clip((dist - inner) / max(outer - inner, 1e-6), 0, 1)
    result = image.copy().astype(np.float32)
    result[..., :3] *= (1.0 - vignette_mask[..., None] * strength)
    return np.clip(result, 0.0, 1.0)


# ─── Film Grain ───

def node_film_grain(image: np.ndarray, amount: float = 0.1, size: float = 1.0,
                    seed: int = 0) -> np.ndarray:
    """Add film grain noise. Simulates analog film texture."""
    rng = np.random.default_rng(seed)
    h, w = image.shape[:2]
    gh = max(1, int(h / max(size, 0.1)))
    gw = max(1, int(w / max(size, 0.1)))
    noise = rng.standard_normal((gh, gw)).astype(np.float32)
    noise = np.repeat(np.repeat(noise, max(1, h // gh), axis=0), max(1, w // gw), axis=1)
    noise = noise[:h, :w]
    noise = noise * amount * 0.25
    result = image.copy().astype(np.float32)
    result[..., :3] += noise[..., None]
    return np.clip(result, 0.0, 1.0)


# ─── Gaussian Blur ───

def _convolve2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Pure NumPy 2D convolution (valid for small kernels)."""
    kh, kw = kernel.shape
    ph, pw = kh // 2, kw // 2
    padded = np.pad(image, ((ph, ph), (pw, pw)), mode='edge')
    h, w = image.shape
    result = np.zeros_like(image, dtype=np.float32)
    for ky in range(kh):
        for kx in range(kw):
            result += padded[ky:ky+h, kx:kx+w] * kernel[ky, kx]
    return result


# ─── Gaussian Blur ───

def _gaussian_kernel(size: int, sigma: float) -> np.ndarray:
    """Generate a 2D Gaussian kernel."""
    x = np.arange(size) - size // 2
    kernel_1d = np.exp(-x * x / (2.0 * sigma * sigma))
    kernel_2d = np.outer(kernel_1d, kernel_1d)
    return kernel_2d / kernel_2d.sum()


def node_blur(image: np.ndarray, size: int = 5, sigma: float = 1.0) -> np.ndarray:
    """Gaussian blur using pure NumPy convolution."""
    if size < 3:
        return image.copy()
    size = size | 1
    kernel = _gaussian_kernel(size, sigma)
    result = image.copy().astype(np.float32)
    for c in range(min(3, result.shape[-1])):
        result[..., c] = _convolve2d(result[..., c], kernel)
    return np.clip(result, 0.0, 1.0)


# ─── Glow / Bloom ───

def node_glow(image: np.ndarray, threshold: float = 0.8, softness: float = 0.5,
              intensity: float = 0.5, size: int = 21) -> np.ndarray:
    """Bloom/glow effect: extract bright areas, blur, composite additively."""
    luma = get_luminance(image[..., :3])
    bright_mask = np.clip((luma - threshold) / max(1.0 - threshold, 1e-6), 0, 1)
    bright = image[..., :3].astype(np.float32) * bright_mask[..., None]
    if size >= 3:
        size = size | 1
        kernel = _gaussian_kernel(size, max(size / 6.0, 1.0))
        for c in range(3):
            bright[..., c] = _convolve2d(bright[..., c], kernel)
    result = image.copy().astype(np.float32)
    blend = softness * intensity
    result[..., :3] += bright * blend
    return np.clip(result, 0.0, 1.0)


# ─── Sharpen ───

def node_sharpen(image: np.ndarray, amount: float = 1.0, radius: float = 1.0,
                 threshold: float = 0.0) -> np.ndarray:
    """Unsharp mask sharpening using pure NumPy."""
    blur_size = max(3, int(radius * 2) | 1)
    sigma = max(0.5, radius)
    kernel = _gaussian_kernel(blur_size, sigma)
    blurred = image[..., :3].copy().astype(np.float32)
    for c in range(3):
        blurred[..., c] = _convolve2d(blurred[..., c], kernel)
    detail = image[..., :3].astype(np.float32) - blurred
    if threshold > 0:
        luma = get_luminance(image[..., :3])
        blur_luma = get_luminance(blurred)
        mask = np.abs(luma - blur_luma) > threshold
        detail *= mask[..., None]
    result = image.copy().astype(np.float32)
    result[..., :3] += detail * amount
    return np.clip(result, 0.0, 1.0)
