# ColorGradingSuite — Complete Architecture & Implementation Plan

## Overview
A professional color grading application that mirrors the **Color Page of DaVinci Resolve 21**.
Built for a single developer using Python + PySide6 + OpenCV + NumPy + OpenGL GLSL.

**Target**: 1080p Full HD on Intel HD 5500 integrated GPU with CPU fallback.

---

## Tech Stack

| Component | Choice | Purpose |
|---|---|---|
| Language | Python 3.14 | Available, rapid prototyping |
| UI Framework | PySide6 (Qt 6.7+) | Dock widgets, QOpenGLWidget, QGraphicsView |
| GPU | OpenGL 3.3 Core GLSL | Real-time per-pixel color operations |
| CPU Fallback | NumPy | Pixel math, LUT interpolation, scopes |
| Video I/O | OpenCV + FFmpeg | Frame-accurate decode, wide format support |
| Image I/O | Pillow | Still import/export (PNG, DPX, EXR, TIFF) |

---

## Complete DaVinci Resolve Color Page Anatomy

### Interface Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  [Gallery / LUTs / Media Pool]         Viewer                [Nodes]│
│  ┌──────────┐                    ┌──────────────┐     ┌──────────┐ │
│  │  Stills  │                    │              │     │  Node    │ │
│  │  Albums  │                    │   Main View  │     │  Editor  │ │
│  │  LUTs    │                    │  (OpenGL)    │     │ ┌──┐    │ │
│  │          │                    │              │     │ │N1│    │ │
│  │          │                    │              │     │ └──┘    │ │
│  └──────────┘                    └──────────────┘     └──────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│  [Thumbnail Timeline]  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │
│  [Mini Timeline]       ═══════════════════════════════════════════  │
├──────────────────────────────────────────────────────────────────────┤
│  Left Palettes (6)  │  Central Palettes (11)    │ Scopes / Key / Info│
│  ┌─────────────────┐│┌────────────────────────┐│┌──────────────────┐│
│  │ Camera Raw      │││ Curves    │ Qualifier  │││ Scopes          ││
│  │ Color Match     │││ ColorSlice│ Window     │││ Keyframe Editor ││
│  │ Primaries       │││ ColorWarp │ Tracker    │││ Info            ││
│  │ HDR             │││           │ Magic Mask ││└──────────────────┘│
│  │ RGB Mixer       │││           │ Blur       ││                   │
│  │ Motion Effects  │││           │ Key        ││                   │
│  └─────────────────┘││           │ Sizing     ││                   │
│                      ││           │ 3D         ││                   │
│                      │└────────────────────────┘│                   │
└──────────────────────────────────────────────────────────────────────┘
```

### Complete Palette Reference

| # | Palette | Location | Function |
|---|---|---|---|
| 1 | **Camera Raw** | Left | RAW decode settings: white balance, ISO, color science per camera type (ARRI, RED, Sony, Canon, Blackmagic, etc.) |
| 2 | **Color Match** | Left | Auto-balance, shot matching, color chart matching (X-Rite, DSC, Datacolor) |
| 3 | **Primaries** | Left | **Color Wheels**: Lift/Gamma/Gain/Offset + master sliders. **Primary Bars**: YRGB channel bars. **Log Wheels**: Shadow/Mid/Highlight in log space. **Adjustment Controls**: Contrast, Pivot, Saturation, Hue, Temperature, Tint, Midtone Detail, Color Boost (Vibrance), Shadows, Highlights |
| 4 | **HDR Palette** | Left | Zone-based HDR grading: customizable tonal ranges, super blacks, specular highlights, Dolby Vision/HDR10+ metadata |
| 5 | **RGB Mixer** | Left | Channel mixing: R→R/G/B, G→R/G/B, B→R/G/B, monochrome, color space conversion presets |
| 6 | **Motion Effects** | Left | Motion blur, optical flow frame blending, noise reduction |
| 7 | **Curves** | Center | **Custom Curves**: Luma + R/G/B individually. **HSL Curves** (6): Hue vs Hue, Hue vs Sat, Hue vs Lum, Lum vs Sat, Sat vs Sat, Sat vs Lum |
| 8 | **ColorSlice** | Center | 6-vector color wheels (R/G/B/C/M/Y) with hue/sat/lum control per vector |
| 9 | **Color Warper** | Center | Grid-based color manipulation: drag hue/saturation in 2D grid |
| 10 | **Qualifier** | Center | HSL/RGB/Luma keyer: eyedropper selection, H/S/L range + softness, 3D preview, clean black/white, matte finesse (blur, erode, dilate) |
| 11 | **Window** | Center | **Power Windows**: Circle, Rectangle, Polygon, Curve (bezier), Gradient. On-screen control handles. Inside/outside/inverted modes |
| 12 | **Tracker** | Center | Point tracker, planar tracker, stabilization. Track modes: pan/tilt/zoom/rotation/3D perspective. Keyframe editing |
| 13 | **Magic Mask** | Center | AI-powered object/person mask. People: body, face, skin. Objects: auto-detect (Studio only) |
| 14 | **Blur** | Center | Gaussian blur, directional blur, motion blur, radial blur. Linked/unlinked X/Y radius |
| 15 | **Key** | Center | Matte post-processing: erode, dilate, blur, softness, highlight/shadow rolloff |
| 16 | **Sizing** | Center | Pan, tilt, zoom, rotate, flip. Input sizing vs output sizing |
| 17 | **3D** | Center | Stereoscopic 3D tools: convergence, left/right eye handling |
| — | **Open FX** | Top-Right | 90+ GPU/CPU accelerated effects: blurs, color effects, glows, lens flares, vignettes, beautification, sharpening, film grain, noise reduction, textures, warpers, restoration |
| — | **Node Editor** | Top-Right | Visual DAG: serial, parallel, layer, splitter/combiner nodes. Node labels, colors, bypass, solo, group |
| — | **Gallery** | Top-Left | Still frames, albums, grade copying, powergrade (.drx) export/import |
| — | **LUT Browser** | Top-Left | LUT library organized by folder, preview before apply |
| — | **Scopes** | Bottom-Right | Waveform (RGB/YRGB/YCbCr), Parade (RGB/YRGB/YCbCr), Vectorscope (with skin tone line), Histogram (RGB/Y/Luma), CIE Chromaticity |
| — | **Keyframes** | Bottom-Right | Animation editor: keyframe list, curve editor, timeline zoom |
| — | **Info** | Bottom-Right | Clip metadata: codec, resolution, frame rate, duration, tags |

---

## Feature Implementation Roadmap (7 Phases)

### PHASE 1 — Application Shell & Video Pipeline
**Goal**: Working app with DaVinci-style layout, video playback with frame-accurate seeking.

| Task | Files | Detail |
|---|---|---|
| 1.1 Dependencies | `requirements.txt` | PySide6, opencv-python, numpy, Pillow |
| 1.2 Entry point | `main.py` | QApplication, MainWindow, show maximized |
| 1.3 Dark theme | `ui/theme/dark_theme.py` | QPalette + QSS: dark gray bg (#1a1a1a), accent blue (#3498db), text (#ccc) |
| 1.4 App state | `ui/app_state.py` | Singleton: current_frame, video_reader, node_graph, selected_node, playback_active |
| 1.5 Video I/O | `core/video_io.py` | OpenCV VideoCapture wrapper: open(), read_frame(idx), total_frames, fps, width, height, close() |
| 1.6 Frame cache | `core/frame_cache.py` | LRU dict: max 120 frames, get/put/clear, QImage storage |
| 1.7 Viewer (OpenGL) | `ui/viewer/viewer_gl.py` | QOpenGLWidget: texture upload, paint frame, zoom (scroll), pan (drag), reset (right-click) |
| 1.8 Thumbnail timeline | `ui/panels/timeline_panel.py` | Horizontal scrollable filmstrip, click-to-seek, playhead indicator |
| 1.9 Mini timeline | `ui/panels/timeline_panel.py` | Track-based timeline below thumbnail strip |
| 1.10 Main Window | `ui/main_window.py` | QMainWindow: 5 dock widget areas, toolbar with transport controls (play/pause/prev/next), menu bar (File/Edit/Color/View/Render) |
| 1.11 Viewer overlays | `ui/viewer/overlays.py` | Grid, safe areas (action/title), guides |
| **Deliverable** | — | Open video → see frames in viewer → play/pause → scrub timeline → zoom/pan |

### PHASE 2 — Primaries Palette
**Goal**: Complete primary color correction with wheels, bars, log, and adjustment controls.

| Task | Files | Detail |
|---|---|---|
| 2.1 Color wheel widget | `ui/widgets/color_wheel_widget.py` | Circular gradient + draggable puck, emits valueChanged(r,g,b) |
| 2.2 Color slider widget | `ui/widgets/color_slider.py` | Gradient bar + draggable handle + numeric label |
| 2.3 Numeric drag | `ui/widgets/numeric_drag.py` | Click-drag on number to adjust, Shift=slow, Ctrl=fast |
| 2.4 Primaries panel | `ui/panels/primaries_panel.py` | 4 wheels (Lift/Gamma/Gain/Offset) + master sliders + reset buttons |
| 2.5 Primary bars | `ui/panels/primaries_panel.py` | Tab switch to bars view: Y/R/G/B channel bars |
| 2.6 Log wheels | `ui/panels/primaries_panel.py` | Tab switch to log view: Shadow/Mid/Highlight wheels |
| 2.7 Adjustment controls | `ui/panels/primaries_panel.py` | Contrast, Pivot, Saturation, Hue, Temp, Tint, Midtone Detail, Color Boost, Shadows, Highlights sliders |
| 2.8 Node base class | `nodes/base_node.py` | Abstract node: inputs, outputs, params, process(), dirty flag |
| 2.9 Color wheel node | `nodes/color_wheel_node.py` | Stores lift/gamma/gain/offset/pivot/contrast/saturation as params |
| 2.10 Node graph engine | `core/node_graph.py` | DAG: add/remove/connect, topological sort, dirty tracking, execute() |
| 2.11 Color math (GPU) | `shaders/color_wheel.glsl` | Lift/Gamma/Gain/Offset per-pixel: `out = ((in+lift)*gain) ^ (1/gamma) + offset` |
| 2.12 Color math (CPU) | `core/color_math.py` | NumPy fallback for lift_gamma_gain(), apply_curve(), rgb_to_hsl(), hsl_to_rgb() |
| 2.13 Eyedropper | `ui/viewer/eyedropper.py` | Click viewer → sample pixel → set white balance or show RGB value |
| 2.14 Common shader utils | `shaders/common.glsl` | rgb2hsl, hsl2rgb, apply_matrix, gamma conversion |
| **Deliverable** | — | Full primary correction: wheels + bars + log + adjustment controls, real-time GPU preview |

### PHASE 3 — Curves & Scopes
**Goal**: Complete curves editor + 5 professional scopes.

| Task | Files | Detail |
|---|---|---|
| 3.1 Curve canvas | `ui/widgets/curve_canvas.py` | Spline editor: drag control points, bezier handles, grid bg, histogram overlay |
| 3.2 Curves panel | `ui/panels/curves_panel.py` | Dropdown: Custom, R, G, B, Hue/Hue, Hue/Sat, Hue/Lum, Lum/Sat, Sat/Sat, Sat/Lum. Reset, eyedropper picker |
| 3.3 Curves node | `nodes/curves_node.py` | Stores curve points per type, builds 256-entry LUT |
| 3.4 Curve shader | `shaders/curves.glsl` | Evaluate curve via texture1D lookup per pixel |
| 3.5 Scope GL base | `ui/widgets/scope_gl.py` | QOpenGLWidget for scope rendering, shared scope framework |
| 3.6 Waveform | `shaders/scope_waveform.glsl` + `ui/panels/scopes_panel.py` | RGB/YRGB/YCbCr modes, intensity accumulation |
| 3.7 Parade | `shaders/scope_parade.glsl` + panel | RGB/YRGB/YCbCr side-by-side |
| 3.8 Vectorscope | `shaders/scope_vectorscope.glsl` + panel | Polar chroma plot, skin tone line, saturation targets |
| 3.9 Histogram | `shaders/scope_histogram.glsl` + panel | RGB/Y/Luma modes, 256 bins |
| 3.10 CIE Chromaticity | `shaders/scope_cie.glsl` + panel | CIE 1931 xy chromaticity, gamut triangle overlay |
| 3.11 Scopes panel | `ui/panels/scopes_panel.py` | Tab widget containing all 5 scopes |
| **Deliverable** | — | Curves affect image in real-time, scopes update on every frame |

### PHASE 4 — Node Graph
**Goal**: Visual node editor with all node types and full graph execution.

| Task | Files | Detail |
|---|---|---|
| 4.1 Node editor panel | `ui/panels/node_editor_panel.py` | QGraphicsView/QGraphicsScene: nodes as rounded rectangles, sockets as circles, edges as bezier curves |
| 4.2 Node Graph engine | `core/node_graph.py` | (extend) topological sort, caching per node, serialization to dict |
| 4.3 All node types | `nodes/*.py` | SerialNode, ParallelNode, LayerNode, SplitterCombiner, ColorWheelNode, CurvesNode, CSTNode, LUTNode, QualifierNode, PowerWindowNode, BlurNode, KeyNode, SizingNode |
| 4.4 Node features | — | Label, color, bypass toggle, solo mode, group, save as preset |
| 4.5 Context menu | — | Right-click: Add Node, Delete, Bypass, Color Label, Copy, Paste |
| 4.6 Graph serialization | `core/project_file.py` | JSON save/load: full node graph state per clip |
| **Deliverable** | — | Full node-based grading: drag nodes, connect, reorder, graph executes |

### PHASE 5 — Secondary Tools
**Goal**: Qualifier, Power Windows, Tracker, Color Warper, ColorSlice.

| Task | Files | Detail |
|---|---|---|
| 5.1 Qualifier panel | `ui/panels/qualifier_panel.py` | Eyedropper selector, H/S/L range bars + softness, 3D key preview toggle, clean black/white, matte finesse |
| 5.2 Qualifier shader | `shaders/qualifier.glsl` | HSL range test per pixel → alpha output |
| 5.3 Qualifier node | `nodes/qualifier_node.py` | HSL params, outputs RGB + alpha |
| 5.4 Power Window panel | `ui/panels/power_window_panel.py` | Shape selector (circle/rect/polygon/curve/gradient), size/pos/rot/feather controls, inside/outside/invert |
| 5.5 Viewer overlays | `ui/viewer/overlays.py` | On-screen shape handles: drag to move, resize, rotate |
| 5.6 Window shader | `shaders/power_window.glsl` | Geometric shape test per pixel → alpha |
| 5.7 Window node | `nodes/power_window_node.py` | Shape params + feather, outputs RGB + alpha |
| 5.8 Tracker panel | `ui/panels/tracker_panel.py` | Track forward/back/reverse, analyze mode (pan/tilt/zoom/rot/3D), keyframe list |
| 5.9 Tracker engine | `core/tracker.py` | NCC template matching, planar homography tracking, keyframe interpolation |
| 5.10 Color Warper | `ui/panels/color_warper_panel.py` | 12×12 grid overlay on color space, drag points to shift hue/sat |
| 5.11 Color Warper shader | `shaders/color_warper.glsl` | Bilinear interpolation of grid deformation |
| 5.12 ColorSlice | `ui/panels/color_slice_panel.py` | 6 vector wheels (R/G/B/C/M/Y) with hue/sat/lum per vector |
| **Deliverable** | — | Full secondary grading: qualifier isolation, power windows, object tracking |

### PHASE 6 — LUTs, Color Management & Effects
**Goal**: LUT support, color space transforms, Resolve FX equivalent.

| Task | Files | Detail |
|---|---|---|
| 6.1 LUT parser | `core/lut_parser.py` | Parse .cube (1D + 3D), .spi1d, .spi3d, .look formats |
| 6.2 LUT manager | `core/lut_manager.py` | Apply 3D LUT (trilinear/tetrahedral), apply 1D LUT, bake grade to LUT |
| 6.3 LUT panel | `ui/panels/lut_panel.py` | Browser: folder tree, thumbnail preview, drag → node |
| 6.4 LUT shader | `shaders/lut_3d.glsl` | Texture3D lookup, trilinear interpolation via hardware |
| 6.5 LUT node | `nodes/lut_node.py` | LUT path, interpolation mode, mix with original |
| 6.6 Color space defs | `core/color_space.py` | Rec709, sRGB, P3D65, ACEScg, ACEScc, ARRI LogC, Sony S-Log3, V-Log, RED Log3G10, Canon Log 2/3. Primaries + transfer functions |
| 6.7 CST shader | `shaders/cst.glsl` | 3×3 matrix + 1×3 offset, log/gamma transfer functions |
| 6.8 CST node | `nodes/cst_node.py` | Input CS, output CS, tone map, HDR/SDR |
| 6.9 Effects browser | `ui/panels/effects_panel.py` | List of built-in effects + drag-to-node |
| 6.10 Built-in FX | `core/effects/` | Blur, Sharpen, Glow, Vignette, Film Grain, Color Space Transform, etc. |
| 6.11 HDR palette | `ui/panels/hdr_panel.py` | Zone wheels: custom tonal range definition, per-zone color/exposure |
| **Deliverable** | — | LUTs + CST + effects working in node graph |

### PHASE 7 — Gallery, Comparison & Export
**Goal**: Polish, workflow, stills, comparison, render.

| Task | Files | Detail |
|---|---|---|
| 7.1 Gallery panel | `ui/panels/gallery_panel.py` | Thumbnail grid, albums, grab still, apply grade, export .drx |
| 7.2 Compare modes | `ui/viewer/compare_mode.py` | Split screen, image wipe, vertical comparison, difference matte, picture-in-picture |
| 7.3 Lightbox | `ui/panels/lightbox.py` | Grid of all timeline clips with grades applied, click to jump |
| 7.4 Keyframe editor | `ui/panels/keyframe_panel.py` | Timeline keyframe list, bezier curve interpolation, copy/paste keyframes |
| 7.5 Project save/load | `core/project_file.py` | JSON schema: clips, node graphs, gallery, settings, color management |
| 7.6 Render/export | `core/renderer.py` | Export current frame (PNG/DPX/EXR), render video via FFmpeg pipe |
| 7.7 Shot matching | `core/color_match.py` | Auto color/contrast matching between clips, color chart detection |
| 7.8 Keyboard shortcuts | `ui/main_window.py` | All shortcuts: Space=play, ←→=frame, I/O=in/out, F=fit, 1-5=scope tabs |
| **Deliverable** | — | Complete professional color grading application |

---

## Color Pipeline Architecture (exact)

```
                    ┌──────────────────────┐
Source Frame ──────▶│  Input Color Space   │  (Camera Raw → Scene Linear)
                    │  Transform (CST)     │
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────────┐
                    │   Node Graph DAG     │
                    │                      │
                    │  ┌─────┐  ┌─────┐   │  Serial: N1→N2→N3
                    │  │ N1  │─▶│ N2  │   │
                    │  └─────┘  └─────┘   │
                    │     │        │       │
                    │     ▼        ▼       │
                    │  ┌─────┐  ┌─────┐   │  Parallel branches
                    │  │ N3  │  │ N4  │   │
                    │  └─────┘  └─────┘   │
                    │      ↘    ↙         │
                    │   ┌────────────┐    │
                    │   │ Layer Mix  │    │  Layer compositing
                    │   └────────────┘    │
                    │                      │
                    │  Each node:          │
                    │  - color_wheel       │
                    │  - curves            │
                    │  - cst               │
                    │  - lut               │
                    │  - qualifier (+α)    │
                    │  - power_window (+α) │
                    │  - blur/sharpen      │
                    │  - key (matte op)    │
                    │  - sizing            │
                    │  - color_slice       │
                    │  - color_warper      │
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────────┐
                    │  Output Color Space  │  (Scene Linear → Timeline CS)
                    │  Transform (CST)     │
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────────┐
                    │  View Transform      │  (Timeline CS → Display CS)
                    │  + Gamut Mapping     │  sRGB / Rec709 / P3 / HDR
                    └──────────┬───────────┘
                               ▼
                        Display Frame
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
                Viewer (GL)       Scopes
                QOpenGLWidget     Waveform, Parade,
                                  Vectorscope, Histogram, CIE
```

### Each Node:

| Property | Type | Description |
|---|---|---|
| `id` | UUID | Unique identifier |
| `type` | str | `color_wheel`, `curves`, `cst`, `lut`, `qualifier`, `window`, `blur`, `key`, `sizing`, `color_slice`, `color_warper` |
| `label` | str | User-defined name |
| `color` | str | Label color (hex) |
| `params` | dict | Node-specific parameters |
| `inputs` | List[Socket] | Input sockets (1-N) |
| `outputs` | List[Socket] | Output sockets (1-N) |
| `bypass` | bool | Skip this node |
| `solo` | bool | Only this node active |
| `enabled` | bool | Toggle on/off |
| `dirty` | bool | Needs re-process |
| `cached_output` | ndarray | Last processed frame |

---

## UI Layout Specification

### Dock Configuration

| Dock | Position | Default Width | Panel |
|---|---|---|---|
| Gallery/LUTs | Top-Left | 280px | TabWidget: Gallery, LUT Browser, Media Pool |
| Viewer | Central | Fill | QOpenGLWidget + Overlays |
| Node Editor | Top-Right | 320px | QGraphicsView + Open FX tab |
| Palettes | Bottom | Full width | Left palettes (6) + Central palettes (11) |
| Timelines | Top (below gallery) | — | Thumbnail strip + Mini timeline |
| Scopes/Keyframes | Bottom-Right | 360px | TabWidget: Scopes, Keyframes, Info |

### Palette Bar Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ [Camera Raw] [ColorMatch] [Primaries] [HDR] [RGBMix] [MotionFX]    │ ← Left palettes
│ [Curves] [ColorSlice] [ColorWarp] [Qualifier] [Window] [Tracker]   │
│ [MagicMask] [Blur] [Key] [Sizing] [3D]                             │ ← Central palettes
└─────────────────────────────────────────────────────────────────────┘
```

Each button opens the corresponding palette panel below it.

---

## Shader Program Summary

| Shader | Inputs | Output | Description |
|---|---|---|---|
| `color_wheel.glsl` | frame, lift/gamma/gain/offset | graded frame | Primary correction |
| `curves.glsl` | frame, curve LUT (256) | graded frame | Curve evaluation |
| `lut_3d.glsl` | frame, 3D LUT texture | graded frame | Trilinear 3D LUT |
| `cst.glsl` | frame, 3×3 matrix, offset | transformed frame | Color space transform |
| `qualifier.glsl` | frame, HSL ranges | frame + alpha | HSL key extraction |
| `power_window.glsl` | frame, shape params | frame + alpha | Mask generation |
| `blur.glsl` | frame, radius, dir | blurred frame | Separable gaussian |
| `color_warper.glsl` | frame, grid | warped frame | Grid color deformation |
| `scope_waveform.glsl` | frame | waveform image | Waveform render |
| `scope_parade.glsl` | frame | parade image | Parade render |
| `scope_vectorscope.glsl` | frame | vectorscope image | Vectorscope render |
| `scope_histogram.glsl` | frame | histogram image | Histogram render |
| `scope_cie.glsl` | frame | CIE image | CIE chromaticity |

---

## Project Structure (Updated)

```
daviciresolve/
├── main.py
├── requirements.txt
│
├── docs/
│   ├── 01_ARCHITECTURE_AND_PLAN.md
│   ├── 02_PALETTE_REFERENCE.md
│   ├── 03_COLOR_SCIENCE.md
│   ├── 04_NODE_REFERENCE.md
│   ├── 05_SHADER_SPEC.md
│   ├── 06_KEYBOARD_SHORTCUTS.md
│   └── 07_USER_GUIDE.md
│
├── core/
│   ├── color_pipeline.py
│   ├── color_math.py
│   ├── color_space.py
│   ├── lut_parser.py
│   ├── lut_manager.py
│   ├── node_graph.py
│   ├── video_io.py
│   ├── frame_cache.py
│   ├── project_file.py
│   ├── preset_manager.py
│   ├── tracker.py
│   ├── color_match.py
│   ├── effects/
│   │   └── __init__.py
│   └── __init__.py
│
├── ui/
│   ├── main_window.py
│   ├── app_state.py
│   │
│   ├── viewer/
│   │   ├── viewer_gl.py
│   │   ├── overlays.py
│   │   ├── compare_mode.py
│   │   └── eyedropper.py
│   │
│   ├── panels/
│   │   ├── camera_raw_panel.py
│   │   ├── color_match_panel.py
│   │   ├── primaries_panel.py
│   │   ├── hdr_panel.py
│   │   ├── rgb_mixer_panel.py
│   │   ├── motion_effects_panel.py
│   │   ├── curves_panel.py
│   │   ├── color_slice_panel.py
│   │   ├── color_warper_panel.py
│   │   ├── qualifier_panel.py
│   │   ├── power_window_panel.py
│   │   ├── tracker_panel.py
│   │   ├── magic_mask_panel.py
│   │   ├── blur_panel.py
│   │   ├── key_panel.py
│   │   ├── sizing_panel.py
│   │   ├── stereoscopic_3d_panel.py
│   │   ├── scopes_panel.py
│   │   ├── node_editor_panel.py
│   │   ├── lut_panel.py
│   │   ├── gallery_panel.py
│   │   ├── lightbox_panel.py
│   │   ├── keyframe_panel.py
│   │   ├── info_panel.py
│   │   ├── effects_panel.py
│   │   └── timeline_panel.py
│   │
│   ├── widgets/
│   │   ├── color_wheel_widget.py
│   │   ├── color_slider.py
│   │   ├── curve_canvas.py
│   │   ├── scope_gl.py
│   │   ├── numeric_drag.py
│   │   ├── gradient_slider.py
│   │   ├── timeline_widget.py
│   │   └── palette_button_bar.py
│   │
│   └── theme/
│       ├── dark_theme.py
│       └── icons/
│
├── nodes/
│   ├── base_node.py
│   ├── serial_node.py
│   ├── parallel_node.py
│   ├── layer_node.py
│   ├── splitter_combiner.py
│   ├── color_wheel_node.py
│   ├── curves_node.py
│   ├── cst_node.py
│   ├── lut_node.py
│   ├── qualifier_node.py
│   ├── power_window_node.py
│   ├── blur_node.py
│   ├── key_node.py
│   ├── sizing_node.py
│   ├── color_slice_node.py
│   └── color_warper_node.py
│
├── shaders/
│   ├── common.glsl
│   ├── color_wheel.glsl
│   ├── curves.glsl
│   ├── lut_3d.glsl
│   ├── cst.glsl
│   ├── qualifier.glsl
│   ├── power_window.glsl
│   ├── blur.glsl
│   ├── color_warper.glsl
│   ├── scope_waveform.glsl
│   ├── scope_parade.glsl
│   ├── scope_vectorscope.glsl
│   ├── scope_histogram.glsl
│   └── scope_cie.glsl
│
├── resources/
│   └── default_cube/
│
├── tests/
│   └── __init__.py
│
└── assets/
    └── icons/
```

---

## Implementation Strategy

### Build Order by Phase

| Phase | Files | Dependencies |
|---|---|---|
| P1: Shell + Video | 11 files | PySide6, OpenCV |
| P2: Primaries | 14 files | P1, NumPy, GLSL |
| P3: Curves + Scopes | 11 files | P2 |
| P4: Node Graph | 20+ files | P2, P3 |
| P5: Secondary | 12 files | P4 |
| P6: LUTs + CST | 10 files | P4 |
| P7: Gallery + Export | 8 files | All above |

### Key Design Principles

1. **Each node is independent** — parameters in, frame out, no side effects
2. **GLSL for speed** — all color ops in shaders, CPU NumPy fallback
3. **Dirty graph traversal** — only re-process nodes that changed
4. **No AI** — Magic Mask will be basic color-difference matte (no ML)
5. **JSON project files** — human-readable, version-controllable
6. **Single-threaded playback** — with async frame pre-fetch
