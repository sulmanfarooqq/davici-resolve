# ColorGradingSuite — User Guide

## Overview

ColorGradingSuite is a professional color grading application modeled after
DaVinci Resolve's Color Page. It provides a complete node-based grading
pipeline with primary correction tools, curves, scopes, qualifiers, power windows,
LUT support, and color management.

---

## Getting Started

### Installation

```bash
# 1. Create virtual environment
cd daviciresolve
python -m venv venv

# 2. Activate (Windows)
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python main.py
```

### Opening Media
- **File → Open** (`Ctrl+O`) — Open a video file
- Supported: MP4, MOV, AVI, ProRes, DNxHD, DPX, EXR, PNG/TIFF sequences
- Drag-and-drop onto the viewer or timeline

### Interface Tour

```
┌──────────────────────────────────────────────────────────────────────┐
│ [Gallery] [LUTs] [Media]              Viewer                 [Nodes]│
│ ┌──────────────┐              ┌────────────────────┐   ┌────────┐  │
│ │ Still frames │              │    Main Image      │   │ Node   │  │
│ │            ▼ │              │   (click-drag pan) │   │ Graph  │  │
│ │              │              │   (scroll zoom)    │   │        │  │
│ └──────────────┘              └────────────────────┘   └────────┘  │
├──────────────────────────────────────────────────────────────────────┤
│  Thumbnail Timeline:  [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]      │
│  Mini Timeline:       ════════════════════════════════════════════   │
├──────────────────────────────────────────────────────────────────────┤
│  [Palette Buttons]     CameraRaw │ Match │ Primaries │ HDR │ ...   │
│  ┌──────────────────────────────────────────────────────────────────┐│
│  │              Active Palette Content Here                        ││
│  └──────────────────────────────────────────────────────────────────┘│
│                              │  Scopes: [Waveform] [Parade] [Vec]  │
│                              │  [Histogram] [CIE]                  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Workflow

### 1. Primary Correction (Primaries Palette)

The first step in any grade. Use the Color Wheels to balance your image:

1. **Offset** first — adjust global brightness
2. **Lift** — set black point and shadow color
3. **Gain** — set white point and highlight color
4. **Gamma** — adjust midtone brightness
5. **Contrast/Saturation** — refine the overall look

**Pro tip:** Watch the Waveform scope — keep skin tones around 70%, blacks
at 0%, whites at 100%.

### 2. Curves for Precision

Switch to the **Curves** palette to shape contrast and color with precision:
- **Luma curve**: S-curve for cinematic contrast
- **Hue vs Sat**: Boost/de-saturate specific colors
- **Hue vs Hue**: Shift specific colors (e.g., blue sky → cyan)

### 3. Node-Based Grading

Build complex grades by chaining nodes:

```
[Input] → [CST: Log→Linear] → [ColorWheel] → [Curves] → [CST: Linear→sRGB] → [Output]
```

**Node types:**
- **Serial** (default): Nodes process in sequence
- **Parallel**: Multiple adjustments blend together
- **Layer**: Foreground/background compositing with alpha
- **Splitter/Combiner**: Process RGB channels independently

### 4. Secondary Correction

#### Qualifier (Color-Based Selection)
1. Click the **Qualifier** palette
2. Click the **eyedropper** in the viewer toolbar
3. Click+drag on the area you want to select
4. Refine with H/S/L range bars
5. Add a correction node after the qualifier node

#### Power Windows (Shape-Based Selection)
1. Click the **Window** palette
2. Choose a shape (circle, rectangle, polygon, curve)
3. Draw the shape in the viewer
4. Adjust feather, rotation, position with on-screen handles
5. Toggle Inside/Outside mode

### 5. Tracking

1. Add a Power Window to the node
2. Click the **Tracker** palette
3. Set the tracker mode (Pan/Tilt/Zoom/Rotation/Perspective)
4. Click **Track Forward** or **Track Reverse**
5. Review track and manually fix keyframes if needed

### 6. LUTs

- **Input LUT**: Apply to first node (log→Rec709 conversion)
- **Creative LUT**: Apply to later node (film look)
- Right-click a node → **LUT** → select from browser
- Adjust **Mix** to control LUT strength

### 7. Comparing Shots

- **Wipe**: Drag across viewer to compare with reference
- **Split Screen**: Display multiple clips side-by-side
- **Gallery**: Grab stills (`Ctrl+G`), apply grades later
- **Shot Match**: Right-click clip → Shot Match to This Clip

---

## Scopes Guide

| Scope | Use |
|---|---|
| **Waveform** | Check exposure: skin tones at ~70%, blacks at 0, whites at 100 |
| **Parade** | Color balance: RGB channels should align at black/white points |
| **Vectorscope** | Skin tone line (~123°): keep skin along this line |
| **Histogram** | Distribution: avoid clipping shadows (left) or highlights (right) |
| **CIE** | Gamut check: ensure colors stay within delivery format |

---

## Keyboard Shortcuts (Quick Reference)

| Key | Action |
|---|---|
| `Space` | Play/Pause |
| `← →` | Frame step |
| `↑ ↓` | 10-frame jump |
| `I` / `O` | In/Out point |
| `F` | Fit viewer |
| `Ctrl+G` | Grab still |
| `Alt+S` | Add serial node |
| `D` | Disable node |
| `S` | Solo node |
| `1`–`0` | Switch palettes |
| `Shift+1`–`5` | Switch scopes |

See `06_KEYBOARD_SHORTCUTS.md` for full list.

---

## Export

- **Frame export** (`Ctrl+E`): Save current frame as PNG/DPX/EXR
- **Video render** (`Ctrl+Shift+E`): Export with grade baked in
- **Grade export**: Right-click node → Save as .colorpreset
- **Project save** (`Ctrl+S`): All node graphs, gallery, settings saved to JSON

---

## Troubleshooting

| Problem | Solution |
|---|---|
| OpenGL viewer black | Update GPU drivers, or disable shaders in Settings → CPU Fallback |
| Video won't open | Install FFmpeg, or convert to MP4 (H.264) |
| Slow playback | Reduce frame cache size in Settings, or use proxy resolution |
| Scopes don't update | Ensure scopes panel is visible (Shift+1-5) |
| Node graph empty | Right-click in node editor → Add Serial Node |

---

## Glossary

| Term | Definition |
|---|---|
| **Lift** | Adjusts shadow tonal range (darkest pixels) |
| **Gamma** | Adjusts midtone tonal range |
| **Gain** | Adjusts highlight tonal range (brightest pixels) |
| **Offset** | Global brightness/color shift affecting all tonal ranges |
| **Pivot** | Luminance center point for contrast adjustment |
| **Color Boost** | Vibrance: intelligently increases saturation of less-saturated areas |
| **Midtone Detail** | Clarity: mid-frequency contrast enhancement |
| **Qualifier** | HSL-based keyer for selecting pixels by color |
| **Power Window** | Geometric mask shape for isolating image regions |
| **Feather** | Soft edge transition of a power window |
| **CST** | Color Space Transform: converts between color spaces |
| **3D LUT** | Three-dimensional lookup table for cross-channel color transforms |
| **CDL** | Color Decision List: ASC standard for primary grade data exchange |
| **DAG** | Directed Acyclic Graph: the node graph execution model |
| **FBO** | Framebuffer Object: OpenGL off-screen render target |
