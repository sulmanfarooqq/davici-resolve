# davici-resolve

**Professional Color Grading Panel — Powered by Blender GPL Color Science**

A standalone, open-source color grading application built with Python, PySide6 (Qt6), and NumPy. All color science algorithms are ported from Blender's GPL compositor source code.

---

## Quick Start

### Windows (One-Click)

```
Double-click setup.bat
```

This will:
1. Create a virtual environment
2. Install all dependencies
3. Run 242 tests
4. Launch the application

### Manual (Any OS)

```bash
git clone https://github.com/sulmanfarooqq/davici-resolve.git
cd davici-resolve
pip install -r requirements.txt
python software/main.py
```

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10, macOS 12, Ubuntu 20.04 | Windows 11, macOS 14, Ubuntu 22.04 |
| **Python** | 3.10+ | 3.12 |
| **RAM** | 4 GB | 8 GB+ |
| **Disk** | 500 MB | 1 GB |
| **GPU** | Any (CPU processing) | Any OpenGL-capable |
| **Display** | 1280x720 | 1920x1080+ |

---

## Features

### Color Grading Tools
- **Lift / Gamma / Gain / Offset** — 4 color wheels
- **Primary Sliders** — Contrast, Saturation, Exposure, Temperature, Tint
- **RGB Curves** — Interactive curve editor with per-channel control
- **Hue Correct** — Hue-based saturation/lightness adjustments
- **ColorSlice** — 6-vector color adjustment (RGB + CMY)
- **Color Warper** — N x N grid-based color remapping
- **Power Windows** — Circle, Rectangle, and Gradient masks
- **Tracker** — OpenCV CSRT object tracking with progress bar

### Effects (25 Node Types)
- Color Balance (LGG / CDL)
- Brightness / Contrast
- Exposure, Gamma, Saturation
- HSV / HSL Adjustment
- Invert, Posterize, Levels
- Shadows / Highlights
- Color Temperature (Bradford adaptation)
- Split Toning
- Vignette, Film Grain
- Gaussian Blur, Glow / Bloom, Sharpen
- Tonemap (Reinhard / Photoreceptor)
- Alpha Over, Pixelate
- 7 Keying nodes (Color, Chroma, Difference, Luminance, Channel, Distance, Spill)
- Blend (20 modes)

### Viewer & Scopes
- **Viewer** — Zoom (scroll), Pan (drag), Fit-to-window, 1:1 view
- **Channel Toggles** — R / G / B / Alpha solo display
- **Color Picker** — Pipette tool for color sampling
- **Waveform** — Luminance waveform display
- **Histogram** — RGB channel histogram
- **Vectorscope** — Color vectorscope with targets

### Project Management
- Save / Load `.daviciproj` files (JSON)
- Recent files menu
- Export frame (PNG / JPEG / TIFF)
- Full undo / redo (50 states)

### Supported Formats
- **Images**: PNG, JPEG, TIFF, BMP, EXR, DPX
- **Video**: MP4, MOV, AVI, MKV, WebM, MXF, MTS
- **LUTs**: .cube (1D and 3D)

---

## Documentation

| Document | Description |
|----------|-------------|
| [Download & Install](DOWNLOAD_AND_INSTALL.md) | Step-by-step installation for all platforms |
| [User Guide](USER_GUIDE.md) | Complete usage guide with screenshots |
| [Keyboard Shortcuts](KEYBOARD_SHORTCUTS.md) | All keyboard shortcuts reference |
| [Node Reference](NODE_REFERENCE.md) | All 25 node types with parameters |
| [Build Standalone .exe](BUILD_EXE.md) | Create a single-file Windows executable |
| [Troubleshooting](TROUBLESHOOTING.md) | Common issues and solutions |

---

## Project Structure

```
davici-resolve/
├── software/                 # Main application
│   ├── main.py              # Entry point
│   ├── core/                # Color science engine
│   │   ├── color_math.py    # 29 Blender-ported functions
│   │   ├── blend_modes.py   # 20 blend modes
│   │   ├── color_correction_nodes.py
│   │   ├── curves_nodes.py
│   │   ├── keying_nodes.py
│   │   ├── additional_nodes.py  # +8 new nodes
│   │   ├── lut_parser.py    # .cube LUT reader
│   │   ├── video_io.py      # OpenCV video reader
│   │   ├── playback_controller.py
│   │   ├── project.py       # .daviciproj save/load
│   │   ├── node_graph.py    # DAG execution engine
│   │   ├── frame_cache.py   # LRU frame cache
│   │   └── undo_manager.py  # 50-state undo stack
│   ├── ui/                  # PySide6 interface
│   │   ├── main_window.py   # Main window (870+ lines)
│   │   ├── panels/          # Color Slice, Warper, Tracker, etc.
│   │   ├── widgets/         # Viewer, Scopes, Node Editor, etc.
│   │   └── theme/           # Dark theme
│   ├── nodes/               # 25 node classes
│   ├── tests/               # 242 tests (all passing)
│   └── build_exe.py         # PyInstaller build script
├── docs/                    # This documentation
├── requirements.txt         # Python dependencies
├── setup.bat                # One-click Windows setup
└── .gitignore
```

---

## License

This project uses color science algorithms ported from Blender, which is licensed under the GNU General Public License v2.0+. The application code in this repository is provided as-is for educational and professional use.

---

## Credits

- **Blender Foundation** — GPL compositor source code (color science algorithms)
- **PySide6** — Qt6 for Python
- **OpenCV** — Video I/O and object tracking
- **NumPy** — Array processing
- **Pillow** — Image I/O
