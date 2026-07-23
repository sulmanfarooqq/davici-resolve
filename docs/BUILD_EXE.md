# Build Standalone .exe

Create a single-file Windows executable that runs without Python installed.

---

## Prerequisites

- Python 3.10+ with all dependencies installed
- ~500 MB free disk space
- Windows 10+ (for building Windows .exe)

---

## Quick Build

```bash
cd software
python build_exe.py
```

The script will:
1. Install PyInstaller if not present
2. Build `dist/davici-resolve.exe` (single file)
3. Print the file size when done

---

## What Happens

```
Installing PyInstaller...
Building davici-resolve.exe...
SUCCESS: dist/davici-resolve.exe
Size: ~85.0 MB
```

The executable bundles:
- Python runtime
- PySide6 (Qt6)
- NumPy
- OpenCV
- Pillow
- All application code

---

## Output

```
software/
└── dist/
    └── davici-resolve.exe    (~85 MB)
```

---

## Distribution

The `.exe` file is self-contained. Users do NOT need Python installed.

To distribute:
1. Copy `dist/davici-resolve.exe` to any Windows machine
2. Double-click to run
3. No installation required

---

## Build Options

The build script can be customized in `software/build_exe.py`:

| Option | Description |
|--------|-------------|
| `--onefile` | Single executable (default) |
| `--windowed` | No console window |
| `--name` | Output filename |
| `--icon` | Custom .ico icon file |

### Add Custom Icon

1. Create or obtain a `.ico` file (256x256 recommended)
2. Save it as `software/icon.ico`
3. Run `python build_exe.py`

The build script automatically detects and uses the icon.

---

## Troubleshooting

### "PyInstaller not found"
The script auto-installs it. If that fails:
```bash
pip install pyinstaller
python build_exe.py
```

### "Build failed" or missing modules
Add hidden imports manually. Edit `build_exe.py` and add:
```python
"--hidden-import", "your_module_name",
```

### Large file size
This is normal. The executable bundles the entire Python runtime plus PySide6/Qt.

### Antivirus false positive
Some antivirus software flags PyInstaller executables. This is a known issue with PyInstaller, not a security threat. You can:
- Add an exception in your antivirus
- Sign the executable with a code signing certificate

---

## Linux / macOS Build

PyInstaller also supports Linux and macOS:

```bash
# Linux
python software/build_exe.py
# Output: software/dist/davici-resolve

# macOS
python software/build_exe.py
# Output: software/dist/davici-resolve.app
```

Note: Build on the target platform. You cannot cross-compile.
