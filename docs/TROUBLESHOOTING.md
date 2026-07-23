# Troubleshooting

Common issues and solutions for davici-resolve.

---

## Installation Issues

### "Python not found" or "python is not recognized"

**Cause**: Python is not installed or not in PATH.

**Fix**:
1. Install Python from https://www.python.org/downloads/
2. **CHECK** "Add Python to PATH" during installation
3. Restart your terminal/command prompt
4. Verify: `python --version`

If you have multiple Python versions:
```bash
py -3.12 --version
# Use py -3.12 instead of python
```

### PySide6 fails to install

**Cause**: Network issues or incompatible Python version.

**Fix**:
```bash
# Try a mirror
pip install PySide6 -i https://mirrors.aliyun.com/pypi/simple/

# Or use a different Python version (3.10-3.12 work best)
# PySide6 does NOT support Python 3.14+
```

### "ModuleNotFoundError: No module named 'PySide6'"

**Cause**: Dependencies not installed in the active Python environment.

**Fix**:
```bash
# Make sure your venv is activated
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Then install
pip install -r requirements.txt
```

### OpenCV import fails

**Cause**: opencv-python not installed or wrong package.

**Fix**:
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python
```

---

## Launch Issues

### "ModuleNotFoundError" on launch

**Cause**: Running from wrong directory or missing `__init__.py` files.

**Fix**:
```bash
# Always run from the project root
cd davici-resolve
python software/main.py

# NOT from inside software/
```

### Application launches but shows black screen

**Cause**: No media loaded.

**Fix**: Load an image or video via File > Open Image/Video.

### "QOpenGLWidget" import error

**Cause**: OpenGL not available in PySide6 installation.

**Fix**: This is handled automatically — the app falls back to QWidget rendering. If you see this error, update PySide6:
```bash
pip install --upgrade PySide6
```

---

## Performance Issues

### Application is slow / laggy

**Causes and fixes**:

1. **Large images**: Reduce image size or use video at lower resolution
2. **Many nodes**: Simplify the node graph
3. **Large blur/glow**: Reduce the `size` parameter
4. **Old hardware**: CPU-only processing, no GPU acceleration yet

### Video playback is choppy

**Cause**: Frame decoding is CPU-bound.

**Fix**:
- Use shorter video clips for editing
- The frame cache helps, but large videos may still lag
- Consider processing single frames instead of real-time playback

---

## Format Issues

### "Could not open video file"

**Cause**: Missing codecs or unsupported format.

**Fix**:
- Ensure OpenCV is properly installed
- Try converting your video to MP4 (H.264) first
- Supported: MP4, MOV, AVI, MKV, WebM, MXF, MTS

### LUT file not loading

**Cause**: Invalid .cube file format.

**Fix**:
- Ensure the file has `.cube` extension
- Check that it starts with `TITLE`, `LUT_3D_SIZE`, or `LUT_1D_SIZE`
- The file should be plain text, not binary

### Image appears corrupted after grading

**Cause**: Float precision overflow.

**Fix**: The application clips values to 0-1 range. If the image looks wrong:
- Reset grade: `Ctrl+R`
- Check extreme slider values
- Reset color wheels

---

## Testing Issues

### "pytest not found"

**Fix**:
```bash
pip install pytest
python -m pytest software/tests/ -v
```

### Tests fail with import errors

**Fix**: Make sure you're running from the project root:
```bash
cd davici-resolve
python -m pytest software/tests/ -v
```

### Some tests fail (not all 242)

**Fix**: Check that all dependencies are installed:
```bash
pip install -r requirements.txt --force-reinstall
python -m pytest software/tests/ -v
```

---

## Node Editor Issues

### Can't connect nodes

**Fix**: Nodes connect by dragging from an output socket (right side) to an input socket (left side). Only matching types can connect (color to color).

### Node graph not restoring from project file

**Fix**: Ensure the project file was saved with the same or compatible version of the application.

---

## Build Issues

### PyInstaller build fails

**Fix**:
```bash
pip install --upgrade pyinstaller
# Clear old builds
rm -rf software/build software/dist
# Rebuild
python software/build_exe.py
```

### .exe doesn't start on another machine

**Cause**: Missing Visual C++ Redistributable.

**Fix**: The target machine may need:
- Microsoft Visual C++ Redistributable (latest)
- Or use the installer from Microsoft

---

## Getting Help

If your issue isn't listed here:

1. Check the [GitHub Issues](https://github.com/sulmanfarooqq/davici-resolve/issues)
2. Run the test suite to verify your setup:
   ```bash
   python -m pytest software/tests/ -v
   ```
3. Open a new issue with:
   - Your OS and Python version
   - The error message
   - Steps to reproduce
