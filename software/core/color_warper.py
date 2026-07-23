"""Color warper processing: bilinear grid interpolation for color remapping."""

import numpy as np


def apply_color_warp(image: np.ndarray, grid: list) -> np.ndarray:
    """Apply grid-based color warping to an image.
    
    The grid is an N×N array where grid[i][j] = [u, v] maps
    input position (i/(N-1), j/(N-1)) to output position (u, v).
    Uses bilinear interpolation for smooth remapping.
    """
    if not grid or not grid[0]:
        return image

    n = len(grid)
    result = image.copy().astype(np.float32)
    h, w = image.shape[:2]

    grid_arr = np.array(grid, dtype=np.float32)

    input_x = np.linspace(0, 1, w, dtype=np.float32)
    input_y = np.linspace(0, 1, h, dtype=np.float32)
    grid_y, grid_x = np.meshgrid(input_y, input_x, indexing='ij')

    cell_x = grid_x * (n - 1)
    cell_y = grid_y * (n - 1)
    ix = np.clip(np.floor(cell_x).astype(int), 0, n - 2)
    iy = np.clip(np.floor(cell_y).astype(int), 0, n - 2)
    fx = cell_x - ix
    fy = cell_y - iy

    for c in range(min(3, result.shape[-1])):
        v00 = grid_arr[iy, ix, c]
        v01 = grid_arr[iy, ix + 1, c]
        v10 = grid_arr[iy + 1, ix, c]
        v11 = grid_arr[iy + 1, ix + 1, c]
        val = (v00 * (1 - fx) * (1 - fy) +
               v01 * fx * (1 - fy) +
               v10 * (1 - fx) * fy +
               v11 * fx * fy)
        result[..., c] = image[..., c] * (1 - val) + val * image[..., c]

    return np.clip(result, 0.0, 1.0)
