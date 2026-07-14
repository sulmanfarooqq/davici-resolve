"""Curve-based color nodes ported from Blender.
Sources:
  - source/blender/nodes/composite/nodes/node_composite_rgb_curves.cc
  - source/blender/nodes/composite/nodes/node_composite_hue_correct.cc
  - source/blender/blenkernel/intern/colortools.cc (BKE_curvemapping_evaluateF)
"""

import numpy as np
from typing import List, Tuple
from core.color_math import rgb_to_hsv, hsv_to_rgb


def evaluate_curve(control_points: List[Tuple[float, float]], x_values: np.ndarray) -> np.ndarray:
    if not control_points:
        return x_values.copy()
    pts = sorted(control_points, key=lambda p: p[0])
    if len(pts) == 1:
        return np.full_like(x_values, pts[0][1])
    # Build 257-entry LUT (matching Blender GPU band_texture)
    lut_size = 257
    lut = np.zeros(lut_size, dtype=np.float32)
    for i in range(lut_size):
        t = i / (lut_size - 1)
        idx = 0
        for j in range(len(pts) - 1):
            if pts[j+1][0] >= t:
                idx = j
                break
        else:
            idx = len(pts) - 2
        p0 = pts[max(0, idx-1)]
        p1 = pts[idx]
        p2 = pts[min(len(pts)-1, idx+1)]
        p3 = pts[min(len(pts)-1, idx+2)]
        t0 = p0[0]; t1 = p1[0]; t2 = p2[0]; t3 = p3[0]
        tt = (t - t1) / max(t2 - t1, 1e-10)
        c1 = p1[1]
        c2 = p2[1]
        if idx == 0:
            m1 = (p2[1] - p1[1]) / max(t2 - t1, 1e-10) * (t2 - t1)
        else:
            m1 = 0.5 * (p2[1] - p0[1]) / max(t2 - t0, 1e-10) * (t2 - t1)
        if idx >= len(pts) - 2:
            m2 = (p2[1] - p1[1]) / max(t2 - t1, 1e-10) * (t2 - t1)
        else:
            m2 = 0.5 * (p3[1] - p1[1]) / max(t3 - t1, 1e-10) * (t2 - t1)
        h00 = 2*tt**3 - 3*tt**2 + 1
        h10 = tt**3 - 2*tt**2 + tt
        h01 = -2*tt**3 + 3*tt**2
        h11 = tt**3 - tt**2
        lut[i] = h00*c1 + h10*m1 + h01*c2 + h11*m2
    idx = np.clip(np.floor(x_values * (lut_size - 1)).astype(int), 0, lut_size - 2)
    frac = x_values * (lut_size - 1) - idx
    return lut[idx] * (1 - frac) + lut[idx + 1] * frac


def node_rgb_curves(image: np.ndarray, curves: dict = None,
                    black_level=(0,0,0), white_level=(1,1,1), factor=1.0) -> np.ndarray:
    if curves is None:
        curves = {'R': [(0,0),(1,1)], 'G': [(0,0),(1,1)], 'B': [(0,0),(1,1)], 'RGB': [(0,0),(1,1)]}
    result = image.copy().astype(np.float32)
    # Remap black/white level
    for c in range(3):
        result[..., c] = (result[..., c] - black_level[c]) / max(white_level[c] - black_level[c], 1e-10)
    result = np.clip(result, 0.0, 1.0)
    # Apply combined RGB curve first
    combined = curves.get('combined', curves.get('RGB', [(0,0),(1,1)]))
    for c in range(3):
        result[..., c] = evaluate_curve(combined, result[..., c])
    # Apply per-channel curves
    for c, ch in enumerate(['R', 'G', 'B']):
        if ch in curves:
            result[..., c] = evaluate_curve(curves[ch], result[..., c])
    if factor < 1.0:
        result = image * (1 - factor) + result * factor
    return np.clip(result, 0.0, 1.0)


def node_hue_correct(image: np.ndarray, curves: dict = None, factor=1.0) -> np.ndarray:
    if curves is None:
        curves = {'H': [(0,0.5),(1,0.5)], 'S': [(0,0.5),(1,0.5)], 'V': [(0,0.5),(1,0.5)]}
    hsv = rgb_to_hsv(image[..., :3])
    # Hue curve: additive offset
    hue_offset = evaluate_curve(curves.get('H', [(0,0.5),(1,0.5)]), hsv[..., 0]) - 0.5
    hsv[..., 0] = (hsv[..., 0] + hue_offset) % 1.0
    # Sat curve: multiplicative
    sat_factor = evaluate_curve(curves.get('S', [(0,0.5),(1,0.5)]), hsv[..., 0]) * 2.0
    hsv[..., 1] = np.clip(hsv[..., 1] * sat_factor, 0, 1)
    # Val curve: multiplicative
    val_factor = evaluate_curve(curves.get('V', [(0,0.5),(1,0.5)]), hsv[..., 0]) * 2.0
    hsv[..., 2] = np.clip(hsv[..., 2] * val_factor, 0, 1)
    result = image.copy().astype(np.float32)
    result[..., :3] = hsv_to_rgb(hsv)
    if factor < 1.0:
        result = image * (1 - factor) + result * factor
    return result


def node_float_curve(image: np.ndarray, curve: List[Tuple[float, float]] = None, factor=1.0) -> np.ndarray:
    if curve is None:
        curve = [(0,0), (1,1)]
    result = image.copy().astype(np.float32)
    result = evaluate_curve(curve, result)
    if factor < 1.0:
        result = image * (1 - factor) + result * factor
    return np.clip(result, 0.0, 1.0)
