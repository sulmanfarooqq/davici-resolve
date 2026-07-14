import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import tempfile, os
import numpy as np
from core.lut_parser import parse_cube, cube_to_lut3d, cube_to_lut1d, apply_lut_3d

CUBE_3D = """TITLE "Test 3D LUT"
LUT_3D_SIZE 2
0.0 0.0 0.0
1.0 0.0 0.0
0.0 1.0 0.0
1.0 1.0 0.0
0.0 0.0 1.0
1.0 0.0 1.0
0.0 1.0 1.0
1.0 1.0 1.0
"""

CUBE_1D = """TITLE "Test 1D LUT"
LUT_1D_SIZE 4
0.0 0.0 0.0
0.3 0.3 0.3
0.7 0.7 0.7
1.0 1.0 1.0
"""

CUBE_INPUT_RANGE = """TITLE "Range"
LUT_3D_SIZE 2
LUT_3D_INPUT_RANGE 0.0 1.0
0.0 0.0 0.0
1.0 0.0 0.0
0.0 1.0 0.0
1.0 1.0 0.0
0.0 0.0 1.0
1.0 0.0 1.0
0.0 1.0 1.0
1.0 1.0 1.0
"""

CUBE_BAD = """not a cube file
"""

def _write_cube(content):
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.cube', delete=False)
    f.write(content)
    f.close()
    return f.name

def test_parse_cube_3d():
    path = _write_cube(CUBE_3D)
    data = parse_cube(path)
    os.unlink(path)
    assert data['title'] == 'Test 3D LUT'
    assert data['type'] == '3D'
    assert data['size'] == 2
    assert len(data['values']) == 8

def test_parse_cube_1d():
    path = _write_cube(CUBE_1D)
    data = parse_cube(path)
    os.unlink(path)
    assert data['title'] == 'Test 1D LUT'
    assert data['type'] == '1D'
    assert data['size'] == 4
    assert len(data['values']) == 4

def test_parse_cube_input_range():
    path = _write_cube(CUBE_INPUT_RANGE)
    data = parse_cube(path)
    os.unlink(path)
    assert data['domain_min'] == [0.0, 0.0, 0.0]
    assert data['domain_max'] == [1.0, 1.0, 1.0]

def test_parse_cube_empty():
    path = _write_cube(CUBE_BAD)
    data = parse_cube(path)
    os.unlink(path)
    assert data['values'] == []

def test_cube_to_lut3d():
    path = _write_cube(CUBE_3D)
    lut = cube_to_lut3d(path)
    os.unlink(path)
    assert lut is not None
    assert lut.shape == (2, 2, 2, 3)

def test_cube_to_lut1d():
    path = _write_cube(CUBE_1D)
    lut = cube_to_lut1d(path)
    os.unlink(path)
    assert lut is not None
    assert lut.shape == (4, 3)

def test_cube_to_lut3d_wrong_type():
    path = _write_cube(CUBE_1D)
    lut = cube_to_lut3d(path)
    os.unlink(path)
    assert lut is None

def test_cube_to_lut1d_wrong_type():
    path = _write_cube(CUBE_3D)
    lut = cube_to_lut1d(path)
    os.unlink(path)
    assert lut is None

def test_apply_lut_3d_identity():
    path = _write_cube(CUBE_3D)
    lut = cube_to_lut3d(path)
    os.unlink(path)
    img = np.array([[[0.0, 0.0, 0.0],
                     [1.0, 0.0, 0.0],
                     [0.0, 1.0, 0.0],
                     [1.0, 1.0, 1.0]]], dtype=np.float32)
    result = apply_lut_3d(img, lut)
    assert result.shape == img.shape
    assert np.allclose(result[0, 0], [0.0, 0.0, 0.0], atol=1e-6)
    assert np.allclose(result[0, 1], [1.0, 0.0, 0.0], atol=1e-6)

def test_apply_lut_3d_clamp():
    path = _write_cube(CUBE_3D)
    lut = cube_to_lut3d(path)
    os.unlink(path)
    img = np.array([[[-0.5, 0.2, 1.5]]], dtype=np.float32)
    result = apply_lut_3d(img, lut)
    assert result.shape == img.shape
    assert np.all(result >= 0.0)
    assert np.all(result <= 1.0)
