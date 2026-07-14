"""LUT parser ported from Blender's node_composite_lut.cc
Supports .cube 1D and 3D LUT files.
"""

import numpy as np
from typing import Optional, Dict, List


def parse_cube(path: str) -> Dict:
    with open(path, 'r') as f:
        lines = f.readlines()
    data = {
        'title': '',
        'type': '3D',
        'size': 33,
        'domain_min': [0.0, 0.0, 0.0],
        'domain_max': [1.0, 1.0, 1.0],
        'values': []
    }
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if line.startswith('TITLE'):
            data['title'] = ' '.join(parts[1:]).strip('"')
        elif line.startswith('LUT_3D_SIZE'):
            data['type'] = '3D'
            data['size'] = int(parts[1])
        elif line.startswith('LUT_1D_SIZE'):
            data['type'] = '1D'
            data['size'] = int(parts[1])
        elif line.startswith('LUT_3D_INPUT_RANGE'):
            data['domain_min'] = [float(parts[1]), float(parts[1]), float(parts[1])]
            data['domain_max'] = [float(parts[2]), float(parts[2]), float(parts[2])]
        else:
            try:
                vals = [float(x) for x in parts[:3]]
                if len(vals) == 3:
                    data['values'].append(vals)
            except ValueError:
                continue
    return data


def cube_to_lut3d(path: str) -> Optional[np.ndarray]:
    data = parse_cube(path)
    if data['type'] != '3D':
        return None
    size = data['size']
    expected = size ** 3
    values = np.array(data['values'][:expected], dtype=np.float32)
    if len(values) < expected:
        return None
    return values.reshape(size, size, size, 3)


def cube_to_lut1d(path: str) -> Optional[np.ndarray]:
    data = parse_cube(path)
    if data['type'] != '1D':
        return None
    size = data['size']
    values = np.array(data['values'][:size], dtype=np.float32)
    if len(values) < size:
        return None
    return values


def apply_lut_3d(image: np.ndarray, lut: np.ndarray) -> np.ndarray:
    size = lut.shape[0]
    c = image.astype(np.float32)
    c = np.clip(c, 0.0, 1.0)
    scale = (size - 1) / size
    offset = 1.0 / (2.0 * size)
    c = c * scale + offset
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    rf = r * (size - 1); gf = g * (size - 1); bf = b * (size - 1)
    r0 = np.clip(np.floor(rf).astype(int), 0, size - 2)
    g0 = np.clip(np.floor(gf).astype(int), 0, size - 2)
    b0 = np.clip(np.floor(bf).astype(int), 0, size - 2)
    fr = rf - r0; fg = gf - g0; fb = bf - b0
    c000 = lut[r0, g0, b0]
    c100 = lut[r0 + 1, g0, b0]
    c010 = lut[r0, g0 + 1, b0]
    c110 = lut[r0 + 1, g0 + 1, b0]
    c001 = lut[r0, g0, b0 + 1]
    c101 = lut[r0 + 1, g0, b0 + 1]
    c011 = lut[r0, g0 + 1, b0 + 1]
    c111 = lut[r0 + 1, g0 + 1, b0 + 1]
    c00 = c000 * (1 - fr[..., None]) + c100 * fr[..., None]
    c10 = c010 * (1 - fr[..., None]) + c110 * fr[..., None]
    c01 = c001 * (1 - fr[..., None]) + c101 * fr[..., None]
    c11 = c011 * (1 - fr[..., None]) + c111 * fr[..., None]
    c0 = c00 * (1 - fg[..., None]) + c10 * fg[..., None]
    c1 = c01 * (1 - fg[..., None]) + c11 * fg[..., None]
    result = c0 * (1 - fb[..., None]) + c1 * fb[..., None]
    return result
