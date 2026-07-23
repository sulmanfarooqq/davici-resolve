# User Guide

Complete guide to using davici-resolve for color grading.

---

## Launching the Application

```bash
python software/main.py
```

Or double-click `setup.bat` on Windows.

The application opens maximized with a dark theme.

---

## Interface Overview

```
┌─────────────────────────────────────────────────────────────┐
│  File  Edit  View                                           │
├────────────────────────────────────────────┬────────────────┤
│                                            │  Node Editor   │
│               VIEWER                       │  Open FX       │
│          (main display area)               │  Gallery       │
│                                            │  LUT Browser   │
│  [Fit] [1:1] [R] [G] [B] [Alpha] [Pick]   │                │
├────────────────────────────────────────────┴────────────────┤
│  [Primaries] [Curves] [Keying] [ColorSlice] [Warper] [Win] │
├──────────────────────────────────┬──────────────────────────┤
│        COLOR PALETTES            │      SCOPES / INFO       │
│   (varies by selected tab)       │  Waveform | Histogram    │
│                                  │  Vectorscope | Info      │
├──────────────────────────────────┴──────────────────────────┤
│  ▶ ⏹ ◀ ▶▶  Frame: 0/0    Speed: 1x          [Status Bar] │
└─────────────────────────────────────────────────────────────┘
```

---

## Loading Media

### Open Image
- **Menu**: File > Open Image
- **Shortcut**: `Ctrl+O`
- Supported: PNG, JPEG, TIFF, BMP, EXR, DPX

### Open Video
- **Menu**: File > Open Video
- **Shortcut**: `Ctrl+Shift+O`
- Supported: MP4, MOV, AVI, MKV, WebM, MXF, MTS

### Open LUT
- **Menu**: File > Open LUT
- **Shortcut**: `Ctrl+L`
- Supported: .cube (1D and 3D)

---

## Color Grading

### Primaries Tab (Default)

**Color Wheels:**
- **LIFT** — Adjusts dark tones (shadows)
- **GAMMA** — Adjusts midtones
- **GAIN** — Adjusts bright tones (highlights)
- **OFFSET** — Adjusts overall color cast

Click and drag inside any wheel to adjust. The white dot shows your current position.

**Sliders:**
- **Contrast** — -1.0 to +1.0 (S-curve at positive values)
- **Saturation** — -1.0 (grayscale) to +1.0 (vivid)
- **Exposure** — -5.0 to +5.0 (EV stops)
- **Temperature** — Warm (positive) to Cool (negative)
- **Tint** — Green (negative) to Magenta (positive)

### Curves Tab
- Interactive RGB curve editor
- Click to add control points
- Drag points to reshape the curve
- Supports per-channel curves (R, G, B) and combined RGB

### Keying Tab
- Color key selection
- Hue / Saturation / Luma range adjustments
- Used for selective color adjustments

### ColorSlice Tab
- 6-vector color adjustment
- Independently adjust RGB and CMY color ranges
- Sliders for each vector: hue, saturation, value

### Color Warper Tab
- Interactive grid-based color remapping
- Click and drag grid points to warp colors
- Useful for precise color-to-color transformations

### Power Windows Tab
- **Circle** — Circular mask with feathering
- **Rectangle** — Rectangular mask
- **Gradient** — Linear gradient mask
- **Tracker** — Track objects through video frames

---

## Viewer Controls

### Zoom & Pan
- **Scroll wheel** — Zoom in/out
- **Left-click drag** — Pan the image
- **Right-click** — Fit to window
- **Fit button** — Fit to window
- **1:1 button** — Actual pixel size

### Channel Toggles
- **R** — Toggle red channel display
- **G** — Toggle green channel display
- **B** — Toggle blue channel display
- **Alpha** — Toggle alpha channel display

When a channel is off, it shows as black in the viewer.

### Color Picker (Pipette)
1. Click the **Pick** button in the viewer toolbar
2. Click anywhere on the image
3. The RGB and HSV values appear in the Info panel
4. Mode auto-disables after picking

---

## Scopes

### Waveform
- Shows luminance distribution from left to right
- Higher = brighter
- Green trace on dark background

### Histogram
- RGB channel distribution
- Red, Green, Blue bars
- Logarithmic scale for better visibility

### Vectorscope
- Shows color distribution (hue and saturation)
- Reference targets for primary colors
- Center = neutral (no color cast)

### Info Panel
- Cursor position (x, y)
- RGB values under cursor
- HSV values under cursor
- Image dimensions, FPS, bit depth

---

## Node Editor

Located in the right panel. The node editor shows the processing chain.

- **Drag nodes** from the palette to add them
- **Connect nodes** by dragging from output to input
- **Bypass** a node by right-clicking it
- **Delete** a node by selecting and pressing Delete
- **Reset** the graph with the Reset button

Available node types (25 total):
Color Balance LGG, Color Balance CDL, Brightness/Contrast, Exposure,
HSV, Gamma, Invert, Posterize, RGB Curves, Hue Correct, Tonemap,
Alpha Over, Levels, Keying, Color Spill, Blend, Pixelate,
Shadows/Highlights, Color Temperature, Split Toning, Vignette,
Film Grain, Blur, Glow, Sharpen

---

## Playback Controls

| Button | Action | Shortcut |
|--------|--------|----------|
| Play/Pause | Toggle playback | `Space` |
| Stop | Stop and return to start | — |
| Step Back | Previous frame | — |
| Step Forward | Next frame | — |
| Speed | Playback speed (0.25x - 4x) | — |

---

## Project Management

### Save Project
- **Menu**: File > Save Project
- **Shortcut**: `Ctrl+S`
- Saves as `.daviciproj` (JSON format)
- Includes: media path, grade parameters, LUT, node graph

### Save As
- **Menu**: File > Save Project As
- **Shortcut**: `Ctrl+Shift+S`

### New Project
- **Menu**: File > New Project
- Resets everything to default

### Open Project
- **Menu**: File > Open Project
- Restores all settings from `.daviciproj` file

### Recent Files
- **Menu**: File > Recent Files
- Shows last 10 opened files

### Export Frame
- **Menu**: File > Export Frame
- Saves current graded frame as PNG, JPEG, or TIFF

---

## Undo / Redo

| Action | Shortcut |
|--------|----------|
| Undo | `Ctrl+Z` |
| Redo | `Ctrl+Shift+Z` |

- 50 undo states maintained
- Captures: all color wheel positions, slider values, LUT state

---

## Gallery

The Gallery tab (right panel) allows you to:
- **Save Still** — Capture the current graded frame
- **Load Still** — Apply a saved still's grade to the current image
- Stills are saved as PNG + JSON sidecar files

---

## LUT Browser

The LUT Browser tab (right panel) allows you to:
- Scan a directory for .cube LUT files
- Preview LUT names in a tree view
- Apply a LUT by double-clicking it

---

## Reset Controls

### Reset Grade
- **Menu**: Edit > Reset Grade
- **Shortcut**: `Ctrl+R`
- Resets all color wheels, sliders, and LUT

### Reset All
- **Menu**: Edit > Reset All
- Resets everything including loaded media

---

## Tips

1. **Start with Primaries** — Set overall look with Lift/Gamma/Gain first
2. **Use Curves for contrast** — More precise than the contrast slider
3. **Check scopes** — Waveform prevents clipping, Vectorscope checks color balance
4. **Save often** — Use `Ctrl+S` to save your project
5. **Use channel toggles** — Isolate R/G/B to check individual channel quality
6. **Color picker** — Use the pipette to sample colors for reference
