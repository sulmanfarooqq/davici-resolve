# davici-resolve — Final Implementation Plan

**Project:** Professional color grading panel (DaVinci Resolve–style)
**Source:** All color math/algos ported from Blender GPL compositor & sequencer source
**Blender source root:** `C:\Users\my\Desktop\daviciresolve\blender`
**Target:** `C:\Users\my\Desktop\daviciresolve\repo_analyze`

---

## 1. Execution Model & Architecture

```
┌─────────────────────────────────────────────────────┐
│                  main.py (launcher)                   │
├─────────────────────────────────────────────────────┤
│                    ui/main_window.py                  │
│   ┌──────────┬──────────┬───────────┬───────────┐   │
│   │  Viewer  │  Wheels  │  Curves   │  Scopes   │   │
│   │  Panel   │  Panel   │  Panel    │  Panel    │   │
│   ├──────────┤          │           │           │   │
│   │ Timeline │          │           │           │   │
│   └──────────┴──────────┴───────────┴───────────┘   │
├─────────────────────────────────────────────────────┤
│       core/ (pure NumPy, CPU pixel processing)       │
│   ┌──────────────┬──────────────┬────────────────┐   │
│   │ color_math   │ lut_parser   │ colormanage    │   │
│   │ (all algos)  │ (.cube LUTs) │ (OCIO wrapper) │   │
│   ├──────────────┴──────────────┴────────────────┤   │
│   │ grading_pipeline (chained node-graph exec)   │   │
│   └─────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────┤
│  shaders/ (GLSL — for future GPU acceleration)       │
│  tests/  (pytest — per-function + per-node tests)   │
└─────────────────────────────────────────────────────┘
```

- **CPU path:** NumPy-vectorized pixel processing (all algorithms)
- **GPU path (future):** GLSL shaders via ModernGL or PyOpenGL
- **Scopes:** Canvas-based rendering of waveform/vectorscope/histogram/RGB-parade
- **Node graph:** DAG-based pipeline with serialization to JSON

---

## 2. PHASE 1 — Core Color Math (Foundation)

### 2.1 Color Conversions (currently partial — expand to full Blender set)
File: `core/color_math_coordinates.py` (new)

| Function | Blender source reference | Status |
|---|---|---|
| `srgb_to_linearrgb` / `linearrgb_to_srgb` | `BLI_math_color_c.hh` | DONE |
| `rgb_to_hsv` / `hsv_to_rgb` | `gpu_shader_common_color_utils.glsl` | DONE |
| `rgb_to_hsl` / `hsl_to_rgb` | same | DONE |
| `rgb_to_yuv_itu_709` / `yuv_to_rgb_itu_709` | same | DONE |
| `rgb_to_yuv_itu_601` | `rgb_to_yuv()` in `math_color.cc` | TODO |
| `rgb_to_ycca_itu_709/601/jpeg` | `gpu_shader_common_color_utils.glsl` | TODO |
| `ycca_to_rgba_itu_709/601/jpeg` | same | TODO |
| `rgb_to_yuva_itu_709` / `yuva_to_rgba_itu_709` | same | TODO |
| `straight_to_premul` / `premul_to_straight` | `BLI_math_color_c.hh` | TODO |
| `get_luminance` (configurable coefs) | `IMB_colormanagement_get_luminance` | DONE (hardcoded) |
| `linearrgb_to_srgb_uchar4` (LUT-accelerated) | `math_color_inline.cc` | TODO |
| `srgb_to_grayscale` | `math_color_inline.cc` | TODO |

### 2.2 ASC CDL (Slope/Offset/Power) — DONE
File: `core/color_math.py`
- `colorbalance_cdl()` — Blender's `offset_power_slope()`
- `colorbalance_lgg()` — Blender's `lift_gamma_gain()`
- Per-channel RGB controls

### 2.3 26 Blend Modes — NEW
File: `core/blend_modes.py`

Port from Blender's `math_color_blend_inline.cc` (1139 lines):
- **All 26 modes:** Mix/Normal, Add, Subtract, Multiply, Screen, Overlay, Hard Light, Soft Light, Color Dodge, Color Burn, Linear Burn, Linear Light, Vivid Light, Pin Light, Darken, Lighten, Difference, Exclusion, Divide, Hue, Saturation, Color, Value/Luminosity, Alpha Over, Alpha Under, Gamma Cross
- Each mode: `blend_<name>(a, b, factor, premultiplied=False) -> np.ndarray`
- **byte variant** (straight alpha, uint8) + **float variant** (premultiplied alpha, float32)
- Confirm against `blender/source/blender/blenlib/intern/math_color_blend_inline.cc`

### 2.4 Blackbody & Wavelength — NEW
File: `core/color_math_blackbody.py`

- `blackbody_temperature_to_rgb(temp)` — Port `IMB_colormanagement_blackbody_temperature_to_rgb()` from `colormanagement.cc` (uses tabulated Planckian locus + CIE 1931 CMFs, 800–12000K)
- `wavelength_to_rgb(wavelength)` — Port `IMB_colormanagement_wavelength_to_rgb()` (380–780nm, CIE 1931 2-degree CMFs, 81-entry table at 5nm spacing)
- `temperature_to_rgb_table(size)` — Generate a linear color ramp table from blackbody

### 2.5 Map Range — NEW
File: `core/color_math_map.py`

- `map_range_linear(value, from_min, from_max, to_min, to_max, clamp=False)`
- `map_range_stepped(value, from_min, from_max, to_min, to_max, steps)`
- `map_range_smoothstep(value, from_min, from_max, to_min, to_max)`
- `map_range_smootherstep(value, from_min, from_max, to_min, to_max)`
- Reference: `node_shader_map_range.cc` (Hermite polynomials for smoothstep/smootherstep)

---

## 3. PHASE 2 — Color Adjustment Nodes (CPU implementations)

Each node is a Python function `f(image, params) -> np.ndarray` operating on float32[0..1] arrays.
All ported from Blender compositor nodes + their GPU shader implementations.

### 3.1 Primary Color Corrections (12 nodes)

| Node | Blender Reference | Params | Priority |
|---|---|---|---|
| **Color Balance (LGG)** | `node_composite_color_balance.cc` — `lift_gamma_gain()` | lift[3], gamma[3], gain[3] | DONE |
| **Color Balance (ASC CDL)** | same — `offset_power_slope()` | slope[3], offset[3], power[3] | DONE |
| **Color Balance (White Point)** | same — `white_point_constant/variable()` | temperature, tint (Bradford adaptation) | TODO |
| **Brightness/Contrast** | `node_composite_brightness_contrast.cc` | brightness(-100..100), contrast(-100..100) — Streidt algo | TODO |
| **Exposure** | `node_composite_exposure.cc` — `color * 2^exposure` | exposure(-10..10) | TODO |
| **Color Correction (3-way)** | `node_composite_color_correction.cc` | master/shadow/midtone/highlight: sat, contrast, gamma, gain, offset; midtones start/end | TODO |
| **HSV** | `node_composite_hue_saturation_value.cc` | hue(0..1), sat(0..2), val(0..2), fac(0..1) | TODO |
| **Gamma** | `node_shader_gamma.cc` — `pow(rgb, gamma)` | gamma(0.001..10) | TODO |
| **Invert** | `node_composite_invert.cc` — `1-color` | fac, invert_color(bool), invert_alpha(bool) | TODO |
| **Posterize** | `node_composite_posterize.cc` — `floor(c*steps)/steps` | steps(2..1024) | TODO |
| **Tonemap (Reinhard)** | `compositor_tone_map_simple.glsl` | key, balance, gamma | TODO |
| **Tonemap (Photoreceptor)** | `compositor_tone_map_photoreceptor.glsl` | intensity, contrast, adaptation, correction (Reinhard & Devlin 2005) | TODO |

### 3.2 Curve-Based Adjustments (3 nodes)

| Node | Blender Reference | Params | Priority |
|---|---|---|---|
| **RGB Curves** | `node_composite_rgb_curves.cc` | 4 curves (R, G, B, Combined), black/white level, fac | TODO |
| **Hue Correct (HSV curves)** | `node_composite_hue_correct.cc` | 3 curves (H, S, V) parameterized by hue, fac | TODO |
| **Float Curve** | `node_shader_curves.cc` — float variant | 1 curve, fac | TODO |

Curve evaluation engine:
- Cubic Hermite interpolation via Catmull-Rom (matching `BKE_curvemapping_evaluateF`)
- Pack curve into 257-entry lookup table (matching Blender's GPU `band_texture`)
- Premultiplied RGB evaluation (`BKE_curvemapping_evaluate_premulRGBF_ex`)

### 3.3 Keying / Matte Nodes (7 + 2 nodes)

| Node | Blender Reference | Priority |
|---|---|---|
| **Color Key** (HSV threshold) | `node_composite_color_key.cc` | TODO |
| **Chroma Key** (YCC angle-based) | `node_composite_chroma_key.cc` — "Video Demystified" | TODO |
| **Difference Key** | `node_composite_difference_key.cc` | TODO |
| **Luminance Key** | `node_composite_luminance_key.cc` | TODO |
| **Channel Key** (per-color-space) | `node_composite_channel_key.cc` (RGB/HSV/YUV/YCbCr) | TODO |
| **Distance Key** (3D euclidean) | `node_composite_distance_key.cc` | TODO |
| **Color Spill** (chromatic despill) | `node_composite_color_spill.cc` | TODO |
| **Keying** (full production keyer) | `node_composite_keying.cc` — chroma preprocess, matte, tweak, garbage/core, postprocess, despill | TODO |
| **Keying Screen** (RBF markers) | `node_composite_keying_screen.cc` | TODO |

### 3.4 Alpha / Compositing Nodes (3 nodes)

| Node | Blender Reference | Priority |
|---|---|---|
| **Alpha Over** (Porter-Duff) | `node_composite_alpha_over.cc` — Over/Disjoint/Conjoint | TODO |
| **Set Alpha** | `node_composite_set_alpha.cc` — Apply Mask / Replace | TODO |
| **Alpha Convert** | `node_composite_alpha_convert.cc` — To Premul / To Straight | TODO |

### 3.5 Convert / Utility Nodes (6 nodes)

| Node | Blender Reference | Priority |
|---|---|---|
| **Separate Color** (RGB/HSV/HSL/YUV/YCbCr) | `node_composite_separate_color.cc` | DONE (partial — RGB only in UI) |
| **Combine Color** (same modes) | `node_composite_combine_color.cc` | TODO |
| **RGB to BW** | `node_composite_rgb_to_bw.cc` — luma dot product | DONE (in scopes) |
| **Normalize** (remap to 0..1) | `node_composite_normalize.cc` | TODO |
| **Levels** (statistical analysis) | `node_composite_levels.cc` — mean, stddev, min, max | TODO |
| **Convert Colorspace** (OCIO) | `node_composite_convert_color_space.cc` | TODO |

---

## 4. PHASE 3 — Color Management (OCIO Integration)

### 4.1 OCIO Color Pipeline
File: `core/colormanage.py` (new)

| Component | Blender Reference | Description |
|---|---|---|
| `ColorSpace` class | `colormanagement.cc` role names | RGB/linear/display colorspace info |
| `colorspace_conversion_matrix` | `colormanage_update_matrices()` | Precomputed 3x3 matrices between common spaces (XYZ, sRGB, Rec.709, Rec.2020, ACES AP0, ACEScg AP1) |
| `display_transform(scene_linear, view, display, look)` | `get_display_buffer_processor()` | scene linear -> [exposure] -> [look] -> [view transform] -> [display space] -> [gamma] -> [dither] |
| `luminance_coefficients` | `IMB_colormanagement_get_luminance_coefficients()` | From OCIO config or BT.709 fallback |
| `whitepoint_from_temp_tint(temp, tint)` | `BLI_math_color.hh` | Planckian locus + isotherm interpolation -> XYZ white |
| `chromatic_adaption_matrix(from_XYZ, to_XYZ)` | `BLI_math_color.hh` | Bradford transform: XYZ->LMS->scale->inv Bradford |

### 4.2 Color Space Matrices

| Matrix | Blender source |
|---|---|
| `xyz_to_scene_linear` / `scene_linear_to_xyz` | `colormanage_update_matrices()` — from OCIO |
| `scene_linear_to_rec709` / `rec709_to_scene_linear` | same |
| `scene_linear_to_rec2020` / `rec2020_to_scene_linear` | same |
| `aces_to_scene_linear` / `scene_linear_to_aces` | same (ACES AP0) |
| `acescg_to_scene_linear` / `scene_linear_to_acescg` | same (ACEScg AP1) |
| `scene_linear_to_srgb_v3` / `srgb_to_scene_linear_v3` | `IMB_colormanagement_scene_linear_to_srgb_v3()` |

Built-in matrices from Blender's `BLI_colorspace.hh`:
- Rec.709: `[[0.412391, 0.357584, 0.180481], [0.212639, 0.715169, 0.072192], [0.019331, 0.119195, 0.950532]]` (to XYZ)
- BT.2020: standard Rec.2020 primaries matrix
- ACES AP0: AP0 primaries to XYZ
- ACEScg AP1: AP1 primaries to XYZ

### 4.3 LUT Management (expand current)
File: `core/lut_parser.py`

| Feature | Status | Notes |
|---|---|---|
| .cube 1D/3D parser | DONE | Full spec compliance |
| Trilinear interpolation | DONE | Blender-matching |
| LUT mix (with factor) | DONE | In main_window.py |
| .csp / .lut / .3dl parser | TODO | Common production LUT formats |
| LUT baking from node graph | TODO | Generate .cube from pipeline |
| Inverse LUT | TODO | For gamut mapping |

---

## 5. PHASE 4 — UI Panels & Widgets

### 5.1 Color Wheels Panel (TAB 0)
File: `ui/widgets/color_wheel.py` (enhance)

| Widget | Status | Enhancements needed |
|---|---|---|
| 4-color wheel layout (Lift/Gamma/Gain/Offset) | DONE | Better puck rendering, numeric input |
| Master slider (per wheel) | TODO | A dark/light slide next to wheel |
| Reset button | DONE | |
| Numeric input fields | TODO | Direct RGB entry per wheel |

### 5.2 Curves Panel (TAB 1) — NEW
File: `ui/widgets/curve_editor.py` (new)

| Feature | Description |
|---|---|
| RGB Curves canvas | Interactive spline editor with 4 curve toggles (R, G, B, RGB combined) |
| HSL Curves canvas | 5 curve modes: Hue vs Hue, Hue vs Sat, Hue vs Lum, Lum vs Sat, Sat vs Sat |
| Curve point CRUD | Click to add, drag to move, right-click to delete |
| Curve presets | Contrast, S-curve, color film look presets |
| Black/White Level inputs | Color pickers for input remapping |
| Grid overlay | 5x5 grid with 25%, 50%, 75%, 100% markers |

### 5.3 Scopes Panel
File: `ui/main_window.py` (lines 494–576 — enhance)

| Scope | Status | Blender algorithm reference |
|---|---|---|
| **Waveform** | DONE (basic) | `gpu_shader_sequencer_scope_comp.glsl` — HDR-aware `scope_to_linear` |
| **Histogram** | DONE (basic, RGB+Luma per channel) | `compositor_levels_sum_color.glsl` — log-scale |
| **Vectorscope** | TODO | YCbCr chroma plane scatter plot |
| **RGB Parade** | TODO | R/G/B waveforms side by side |

Enhancements:
- Scope source selection: Input / Output / Luma / Chroma
- Gamut boundary overlay on vectorscope
- CIE chromaticity diagram
- Zebra pattern (`gpu_shader_sequencer_zebra_frag.glsl`)

### 5.4 Keying Panel (TAB 2 alt) — NEW
File: `ui/widgets/keying_panel.py` (new)

- Key color picker (eyedropper)
- Threshold / Falloff sliders per key type
- Matte view toggle (show matte instead of color)
- Despill strength / balance

### 5.5 Timeline / Stills — NEW
File: `ui/widgets/timeline.py` (new)

- Current grade save/load as stills
- Gallery of saved stills (split-screen comparison)
- Grade copy/paste between stills

### 5.6 Viewer Enhancements
File: `ui/main_window.py` (viewer section)

| Feature | Status |
|---|---|
| Fit / 1:1 zoom | DONE |
| Pan (drag when zoomed) | TODO |
| Split-screen: Before/After (left-right or wipe) | TODO |
| RGB channel solo (R/G/B on/off toggle) | TODO |
| Gamut warning (highlight out-of-gamut pixels) | TODO |
| Input LUT preview | TODO |

---

## 6. PHASE 5 — Node Graph Pipeline

### 6.1 Pipeline Architecture
File: `core/grading_pipeline.py` (new)

```
Node Graph (DAG):
  InputImage -> [Lift/Gamma/Gain] -> [RGB Curves] -> [Keying] -> [Output]
                \___________________________________________/
                factor-mix with original (optional)
```

- `Node` base class: `__init__(params)`, `apply(image) -> image`
- `NodeGraph` class: list of nodes, serialization to/from JSON
- `Pipeline` class: ordered list or DAG executor
- Grade serialization: JSON with node type + param values

### 6.2 Node Types (all from Phase 2)
- All color adjustment nodes as `PipelineNode` subclasses
- Node type registry: `{'name': Type, ...}` for serialization
- Ctrl+Drag to reorder in graph

### 6.3 Grade State Management
```python
class GradeState:
    nodes: List[Node]        # All nodes in pipeline
    active_node: int         # Currently editing
    stills: Dict[str, dict]  # Saved grade snapshots
    history: List[dict]      # Undo stack
```

---

## 7. PHASE 6 — Effects & Polish

### 7.1 Glare / Bloom — NEW
File: `core/effect_glare.py`

Port from Blender's `compositor_glare_*.glsl` shaders:
- **Bloom:** Downsample → blur → upsample → add
- **Ghosts:** Affine-transformed copies of highlights
- **Streaks:** Directional recursive filters
- **Fog Glow:** Wide gaussian
- **Simple Star:** 4-directional star filter
- Parameters: threshold, clamp, strength, saturation, tint

### 7.2 Glow Effect — NEW
File: `core/effect_glow.py`

Port from Blender's sequencer `effect_glow.cc`:
- Isolate highlights above threshold
- 2-pass Gaussian blur
- Composite back with original

### 7.3 Filter Nodes — NEW
File: `core/filter_nodes.py`

| Filter | Reference | Priority |
|---|---|---|
| Gaussian Blur | `node_composite_blur.cc` | MEDIUM |
| Bilateral Blur | `node_composite_bilateral_blur.cc` | LOW |
| Bokeh Blur | `node_composite_bokeh_blur.cc` | LOW |
| Defocus | `node_composite_defocus.cc` | LOW |
| Dilate/Erode | `node_composite_dilate_erode.cc` | MEDIUM |
| Despeckle (Median) | `node_composite_despeckle.cc` | LOW |
| Kuwahara | `node_composite_kuwahara.cc` | LOW |

### 7.4 Keyboard Shortcuts
File: `docs/06_KEYBOARD_SHORTCUTS.md`

| Shortcut | Action | Status |
|---|---|---|
| Ctrl+O | Open image | DONE |
| Ctrl+L | Load LUT | DONE |
| Ctrl+Q | Quit | DONE |
| Ctrl+R | Reset grade | DONE |
| Ctrl+Z | Undo | TODO |
| Ctrl+Shift+Z | Redo | TODO |
| Ctrl+C / V | Copy/paste grade | TODO |
| Ctrl+S | Save grade | TODO |
| 1-4 | Tab switch | TODO |
| Space | Play/pause (future: timeline) | TODO |
| Alt+Click | Color picker sample | TODO |

---

## 8. Test Plan
File: `tests/`

| Test file | What it tests | Priority |
|---|---|---|
| `test_color_math.py` | All color conversions (HSV, HSL, YUV, YCbCr, sRGB/linear) | HIGH |
| `test_blend_modes.py` | All 26 blend modes against Blender reference values | HIGH |
| `test_nodes_color.py` | Each node: color_balance, bright_contrast, exposure, etc. | HIGH |
| `test_nodes_keying.py` | All 9 keying node implementations | HIGH |
| `test_colormanage.py` | Color space matrices, display transform, whitepoint | HIGH |
| `test_lut.py` | .cube parsing, trilinear interpolation accuracy | HIGH |

Test methodology:
- Golden images from Blender render output for each node
- Per-pixel tolerance: float32 nodes, epsilon ≤ 1e-6
- Vectorized comparison: `np.allclose(expected, actual, atol=1e-6)`

Run tests via:
```bash
pytest tests/ -v
```

---

## 9. Phase Timeline

| Phase | Contents | Estimated files | Dependencies |
|---|---|---|---|
| **P1** | Core color math + blend modes + blackbody | 4 files | None |
| **P2a** | 12 primary color correction nodes | 3 files | P1 |
| **P2b** | 9 keying nodes + 3 alpha nodes | 3 files | P1 |
| **P2c** | 6 convert/utility nodes + curves engine | 3 files | P1 |
| **P3** | OCIO color management pipeline | 2 files | P1 |
| **P4** | UI widgets: curves editor, keying panel, scopes, timeline | 5 files | P2, P3 |
| **P5** | Node graph pipeline + serialization | 2 files | P2, P4 |
| **P6** | Effects (glare, glow, filters) + polish | 4 files | P5 |

---

## 10. File Manifest (Complete)

```
repo_analyze/
├── main.py                          # Launcher (DONE)
├── requirements.txt                 # numpy, pillow (DONE)
│
├── core/
│   ├── __init__.py                  # (DONE)
│   ├── color_math.py                # LGG, ASC CDL, HSV/HSL/YUV, contrast/sat/temp (DONE, expand)
│   ├── color_math_coordinates.py    # YCbCr, YUV_601, premul/straight, LUT-accelerated sRGB (NEW)
│   ├── color_math_blackbody.py      # Blackbody temp→RGB, wavelength→RGB (NEW)
│   ├── color_math_map.py            # Map range (linear, stepped, smoothstep) (NEW)
│   ├── blend_modes.py               # 26 blend modes, byte + float (NEW)
│   ├── colormanage.py               # OCIO pipeline, matrices, whitepoint (NEW)
│   ├── color_correction_nodes.py    # 12 primary color nodes (PARTIAL)
│   ├── keying_nodes.py              # 9 keying + 3 alpha + 6 utility nodes (NEW)
│   ├── curves_nodes.py              # RGB curves + hue correct + float curve + curve engine (NEW)
│   ├── effect_glare.py              # Glare/bloom (NEW)
│   ├── effect_glow.py               # Glow effect (NEW)
│   ├── filter_nodes.py              # Blur, dilate/erode, despeckle, etc. (NEW)
│   ├── grading_pipeline.py          # Node graph DAG, serialization (NEW)
│   ├── lut_parser.py                # .cube parser, trilinear interp (DONE, expand)
│   └── ...                          # Additional format parsers
│
├── ui/
│   ├── __init__.py                  # (DONE)
│   ├── main_window.py               # App, viewer, scopes (DONE, enhance)
│   ├── widgets/
│   │   ├── __init__.py              # (DONE)
│   │   ├── color_wheel.py           # Lift/Gamma/Gain/Offset wheel (DONE, enhance)
│   │   ├── curve_editor.py          # Interactive curve editor (NEW)
│   │   ├── keying_panel.py          # Keying controls (NEW)
│   │   └── timeline.py              # Stills/gallery (NEW)
│   └── ...
│
├── shaders/
│   ├── color_balance.glsl           # (DONE)
│   ├── color_correction.glsl        # (NEW)
│   ├── keying.glsl                  # (NEW)
│   └── ...                          # Additional GLSL for GPU path
│
├── tests/
│   ├── test_color_math.py           # (NEW)
│   ├── test_blend_modes.py          # (NEW)
│   ├── test_nodes_color.py          # (NEW)
│   ├── test_nodes_keying.py         # (NEW)
│   ├── test_colormanage.py          # (NEW)
│   └── test_lut.py                  # (NEW)
│
└── docs/
    ├── 01_ARCHITECTURE_AND_PLAN.md  # (DONE)
    ├── ...                          # (all 9 docs DONE)
    └── 09_UI_DESIGN_SPEC.md         # (DONE)
```

---

## 11. Blender Source Reference Index

### Compositor Nodes
| Node | Blender path |
|---|---|
| Color Balance (LGG+CDL+White) | `blender/source/blender/nodes/composite/nodes/node_composite_color_balance.cc` |
| Bright/Contrast | `.../node_composite_brightness_contrast.cc` |
| Color Correction (3-way) | `.../node_composite_color_correction.cc` |
| Exposure | `.../node_composite_exposure.cc` |
| RGB Curves | `.../node_composite_rgb_curves.cc` |
| Hue Correct | `.../node_composite_hue_correct.cc` |
| HSV | `.../node_composite_hue_saturation_value.cc` |
| Tonemap | `.../node_composite_tone_map.cc` |
| Invert | `.../node_composite_invert.cc` |
| Posterize | `.../node_composite_posterize.cc` |
| Levels | `.../node_composite_levels.cc` |
| Combine/Separate Color | `.../node_composite_combine_color.cc` / `separate_color.cc` |
| RGB to BW | `.../node_composite_rgb_to_bw.cc` |
| Convert Colorspace | `.../node_composite_convert_color_space.cc` |
| Convert to Display | `.../node_composite_convert_to_display.cc` |
| Alpha Over | `.../node_composite_alpha_over.cc` |
| Set Alpha | `.../node_composite_set_alpha.cc` |
| Alpha Convert | `.../node_composite_alpha_convert.cc` |
| Color Key | `.../node_composite_color_key.cc` |
| Chroma Key | `.../node_composite_chroma_key.cc` |
| Difference Key | `.../node_composite_difference_key.cc` |
| Luminance Key | `.../node_composite_luminance_key.cc` |
| Channel Key | `.../node_composite_channel_key.cc` |
| Distance Key | `.../node_composite_distance_key.cc` |
| Color Spill | `.../node_composite_color_spill.cc` |
| Keying (full) | `.../node_composite_keying.cc` |
| Keying Screen | `.../node_composite_keying_screen.cc` |
| Normalize | `.../node_composite_normalize.cc` |
| Glare | `.../node_composite_glare.cc` |

### GPU Shaders
| Shader | Blender path |
|---|---|
| Color Balance | `blender/source/blender/compositor/shaders/library/gpu_shader_compositor_color_balance.glsl` |
| Bright/Contrast | `.../gpu_shader_compositor_bright_contrast.glsl` |
| Color Correction | `.../gpu_shader_compositor_color_correction.glsl` |
| Exposure | `.../gpu_shader_compositor_exposure.glsl` |
| HSV | `.../gpu_shader_compositor_hue_saturation_value.glsl` |
| Hue Correct | `.../gpu_shader_compositor_hue_correct.glsl` |
| Invert | `.../gpu_shader_compositor_invert.glsl` |
| Posterize | `.../gpu_shader_compositor_posterize.glsl` |
| Alpha Over | `.../gpu_shader_compositor_alpha_over.glsl` |
| Set Alpha | `.../gpu_shader_compositor_set_alpha.glsl` |
| Convert Alpha | `.../gpu_shader_compositor_convert_alpha.glsl` |
| Color to Luminance | `.../gpu_shader_compositor_color_to_luminance.glsl` |
| Separate/Combine Color | `.../gpu_shader_compositor_separate_combine.glsl` |
| Color Matte | `.../gpu_shader_compositor_color_matte.glsl` |
| Chroma Matte | `.../gpu_shader_compositor_chroma_matte.glsl` |
| Channel Matte | `.../gpu_shader_compositor_channel_matte.glsl` |
| Difference Matte | `.../gpu_shader_compositor_difference_matte.glsl` |
| Distance Matte | `.../gpu_shader_compositor_distance_matte.glsl` |
| Luminance Matte | `.../gpu_shader_compositor_luminance_matte.glsl` |
| Color Spill | `.../gpu_shader_compositor_color_spill.glsl` |
| Color Utils (HSV/HSL/YUV/YCbCr) | `blender/source/blender/gpu/shaders/common/gpu_shader_common_color_utils.glsl` |
| Mix/Blend Modes | `blender/source/blender/gpu/shaders/common/gpu_shader_common_mix_rgb.glsl` |

### Full Compute Shaders
| Shader | Blender path |
|---|---|
| Tone Map Simple | `blender/source/blender/compositor/shaders/compositor_tone_map_simple.glsl` |
| Tone Map Photoreceptor | `.../compositor_tone_map_photoreceptor.glsl` |
| Gamma Correct | `.../compositor_gamma_correct.glsl` |
| Keying Compute Matte | `.../compositor_keying_compute_matte.glsl` |
| Keying Compute Image | `.../compositor_keying_compute_image.glsl` |
| Keying Extract Chroma | `.../compositor_keying_extract_chroma.glsl` |
| Keying Replace Chroma | `.../compositor_keying_replace_chroma.glsl` |
| Keying Screen | `.../compositor_keying_screen.glsl` |
| Keying Tweak Matte | `.../compositor_keying_tweak_matte.glsl` |
| Glare Highlights | `.../compositor_glare_highlights.glsl` |
| Glare Mix | `.../compositor_glare_mix.glsl` |

### Core Color Math (BLI)
| File | Blender path |
|---|---|
| Color blends (26 modes) | `blender/source/blender/blenlib/intern/math_color_blend_inline.cc` |
| Color conversions | `blender/source/blender/blenlib/intern/math_color.cc` |
| sRGB/linear w/ SIMD | `blender/source/blender/blenlib/intern/math_color_inline.cc` |
| Color blend declarations | `blender/source/blender/blenlib/BLI_math_color_blend.hh` |
| Color conversions decl | `blender/source/blender/blenlib/BLI_math_color_c.hh` |
| Color C++ templates | `blender/source/blender/blenlib/BLI_math_color.hh` |
| Color space matrices | `blender/source/blender/blenlib/BLI_colorspace.hh` |

### Color Management
| File | Blender path |
|---|---|
| Colormanagement main | `blender/source/blender/imbuf/intern/colormanagement.cc` (3914 lines) |
| Rect operations (blend) | `blender/source/blender/imbuf/intern/rectop.cc` |
| Image filter | `blender/source/blender/imbuf/intern/filter.cc` |
| Image transform | `blender/source/blender/imbuf/intern/transform.cc` |

### Sequencer Strips & Modifiers
| File | Blender path |
|---|---|
| Color Balance modifier | `blender/source/blender/sequencer/intern/modifiers/MOD_color_balance.cc` |
| Curves modifier | `.../MOD_curves.cc` |
| Hue Correct modifier | `.../MOD_hue_correct.cc` |
| Bright/Contrast modifier | `.../MOD_brightness_contrast.cc` |
| White Balance modifier | `.../MOD_white_balance.cc` |
| Tonemap modifier | `.../MOD_tonemap.cc` |
| Glow effect | `blender/source/blender/sequencer/intern/effects/effect_glow.cc` |

---

## 12. Key Algorithms — Implementation Notes

### Curve Evaluation (matching Blender's `BKE_curvemapping_evaluateF`)
```python
def evaluate_curve(control_points, x):
    # Build Catmull-Rom spline from control points
    # Pack into 257-entry table (GPU band_texture style)
    # Index: idx = int(x * 256)
    # Blend: frac = x * 256 - idx
    # Result: table[idx] * (1-frac) + table[idx+1] * frac
```

### Color Correction 3-Way (matching Blender's tonal range split)
```python
def color_correction_3way(image, shadows, midtones, highlights, midtones_start, midtones_end):
    luma = get_luminance(image)
    # Shadow weight: 1.0 at 0, 0.0 at midtones_start (10% margin)
    # Highlight weight: 1.0 at 1, 0.0 at midtones_end (10% margin)
    # Midtone weight: 1.0 - shadow_weight - highlight_weight
    # Each range: sat → contrast → gamma → gain → offset
    # Combine: result = shadow * shadow_w + midtone * midtone_w + highlight * highlight_w
```

### Tone Mapping (Reinhard & Devlin 2005)
```python
def tonemap_photoreceptor(image, intensity, contrast, adaptation, correction):
    lav = exp(mean(log(max(luminance, 1e-6))))  # log-average luminance
    cav = geometric_mean_per_channel(image)       # per-channel adaptation
    key = 1 / (1 + exp(-(lav - offset) * slope)) # auto-key
    al = lerp(lerp(lav, luminance, adaptation), cav, correction)  # adaptation level
    return image / (image + (intensity * al) ** contrast)
```

### Keying Pipeline (matching Blender's full keyer)
```python
def keying(image, key_color, blur_size, balance, black_level, white_level,
           edge_detection, garbage_matte, core_matte, despill_strength):
    # 1. (Optional) Blur chroma in YCC space
    # 2. Compute matte: saturation comparison with key color
    # 3. Tweak matte: black/white levels + edge detection
    # 4. Combine garbage/core mattes
    # 5. Postprocess: blur/dilate/feather
    # 6. Despill: reduce dominant channel relative to others
```

---

## 13. Deliverables Summary

| Category | Count |
|---|---|
| Core color math functions | 35+ |
| Blend modes (byte + float) | 26 × 2 = 52 |
| Color correction nodes | 12 |
| Curve-based nodes | 3 |
| Keying/matte nodes | 9 |
| Alpha/compositing nodes | 3 |
| Convert/utility nodes | 6 |
| Effects nodes | 5 |
| Color management module | 1 |
| UI widgets (new) | 3 |
| UI enhancements | 5+ |
| Test files | 6 |
| **Total new files** | **~25** |
| **Total functions** | **~120** |
