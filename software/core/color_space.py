"""Color space definitions and conversion matrices.
Ported from Blender's source/blender/blenlib/BLI_colorspace.hh
and source/blender/imbuf/intern/colormanagement.cc
"""

import numpy as np
from typing import Tuple, Optional

# ─── Matrix definitions ───

# Rec.709 (sRGB) primaries to XYZ (D65)
REC709_TO_XYZ = np.array([
    [0.412391, 0.357584, 0.180481],
    [0.212639, 0.715169, 0.072192],
    [0.019331, 0.119195, 0.950532]
])
XYZ_TO_REC709 = np.linalg.inv(REC709_TO_XYZ)

# Rec.2020 primaries to XYZ
REC2020_TO_XYZ = np.array([
    [0.636958, 0.144617, 0.168881],
    [0.262700, 0.677998, 0.059302],
    [0.000000, 0.028073, 1.060985]
])
XYZ_TO_REC2020 = np.linalg.inv(REC2020_TO_XYZ)

# ACES AP0 to XYZ
ACES_AP0_TO_XYZ = np.array([
    [0.952552, 0.000000, 0.000094],
    [0.343989, 0.728197, -0.072186],
    [0.000000, 0.000000, 1.008825]
])
XYZ_TO_ACES_AP0 = np.linalg.inv(ACES_AP0_TO_XYZ)

# ACEScg (AP1) to XYZ
ACESCG_TO_XYZ = np.array([
    [0.662454, 0.134004, 0.156188],
    [0.272229, 0.674082, 0.053690],
    [-0.005574, 0.004060, 1.010339]
])
XYZ_TO_ACESCG = np.linalg.inv(ACESCG_TO_XYZ)

# DCI P3 to XYZ
P3D65_TO_XYZ = np.array([
    [0.486571, 0.265668, 0.198217],
    [0.228975, 0.691739, 0.079287],
    [0.000000, 0.045113, 1.043944]
])
XYZ_TO_P3D65 = np.linalg.inv(P3D65_TO_XYZ)

# Luminance coefficients
LUMA_BT709 = np.array([0.2126, 0.7152, 0.0722])
LUMA_BT2020 = np.array([0.2627, 0.6780, 0.0593])


class ColorSpace:
    def __init__(self, name: str, to_xyz: np.ndarray, from_xyz: np.ndarray,
                 transfer: str = "linear", primaries: str = "rec709"):
        self.name = name
        self.to_xyz = to_xyz
        self.from_xyz = from_xyz
        self.transfer = transfer
        self.primaries = primaries

    def convert_to(self, rgb: np.ndarray, target: 'ColorSpace') -> np.ndarray:
        if self == target:
            return rgb
        xyz = self.to_xyz @ rgb[..., :3, None]
        xyz = xyz[..., 0]
        result = target.from_xyz @ xyz[..., None]
        out = rgb.copy()
        out[..., :3] = result[..., 0]
        if self.transfer == target.transfer:
            return out
        return out


COLOR_SPACES = {
    "scene_linear": ColorSpace("Scene Linear", np.eye(3), np.eye(3), "linear", "rec709"),
    "rec709": ColorSpace("Rec.709", REC709_TO_XYZ, XYZ_TO_REC709, "linear", "rec709"),
    "srgb": ColorSpace("sRGB", REC709_TO_XYZ, XYZ_TO_REC709, "srgb", "rec709"),
    "rec2020": ColorSpace("Rec.2020", REC2020_TO_XYZ, XYZ_TO_REC2020, "linear", "rec2020"),
    "aces_ap0": ColorSpace("ACES AP0", ACES_AP0_TO_XYZ, XYZ_TO_ACES_AP0, "linear", "aces_ap0"),
    "acescg": ColorSpace("ACEScg", ACESCG_TO_XYZ, XYZ_TO_ACESCG, "linear", "acescg"),
    "p3d65": ColorSpace("P3-D65", P3D65_TO_XYZ, XYZ_TO_P3D65, "linear", "p3d65"),
}


def get_colorspace(name: str) -> Optional[ColorSpace]:
    return COLOR_SPACES.get(name.lower())


def convert_colorspace(rgb: np.ndarray, from_cs: str, to_cs: str) -> np.ndarray:
    src = get_colorspace(from_cs)
    dst = get_colorspace(to_cs)
    if src is None or dst is None:
        return rgb
    return src.convert_to(rgb, dst)


def srgb_transfer_forward(linear: np.ndarray) -> np.ndarray:
    mask = linear <= 0.0031308
    return np.where(mask, linear * 12.92, 1.055 * np.power(np.maximum(linear, 0.0), 1.0 / 2.4) - 0.055)


def srgb_transfer_inverse(encoded: np.ndarray) -> np.ndarray:
    mask = encoded <= 0.04045
    return np.where(mask, encoded / 12.92, np.power((np.maximum(encoded, 0.0) + 0.055) / 1.055, 2.4))
