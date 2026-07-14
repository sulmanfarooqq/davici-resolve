# Updated Plan: Build on Blender's Open Source Color Grading Engine

## The Strategy

Instead of writing every color algorithm from scratch, we **directly use Blender's GPL-licensed
source code** — specifically its compositor nodes, GLSL shaders, and color management pipeline.
Blender's color grading IS production-grade (used in Spider-Man, Dune, The Mandalorian).
We port/copy what we need, build a lightweight UI around it.

### What Blender Gives Us (for free, GPL)

| Feature | Blender Source File | What We Get |
|---|---|---|
| **Lift/Gamma/Gain** | `node_composite_color_balance.cc` | Full ASC CDL + LGG math, white balance |
| **Color Balance GPU** | `gpu_shader_compositor_color_balance.glsl` | GLSL shader (~400 lines) |
| **RGB Curves** | `node_composite_curves.cc` + `gpu_shader_compositor_curves.glsl` | Spline evaluation + histogram |
| **Hue Correct** | `node_composite_hue_correct.cc` + GLSL | Hue/Sat/Val curves |
| **Mix/Blend** | `node_composite_mix.cc` + GLSL | 26 blend modes |
| **Color Math** | `gpu_shader_common_color_utils.glsl` | RGB↔HSV↔HSL↔YUV conversions |
| **Keying** | `node_composite_color_matte.cc` + `gpu_shader_compositor_color_matte.glsl` | Chroma/Luma/HSV key |
| **Blur** | `node_composite_blur.cc` + GLSL | Gaussian, directional, fast blur |
| **Color Management** | `IMB_colormanagement.cc` + OCIO config | Full ACES, Rec709, LogC, SLog3 etc. |
| **Track/Stabilize** | `node_composite_track.cc` + `node_composite_plane_track.cc` | Point + planar tracking |
| **LUT** | `node_composite_lut.cc` | 1D + 3D LUT (.cube) |
| **Pixel Math** | `COM_*Algorithm.h` | Flood fill, convolution, morphology |

### The Math is Trivially Simple

Blender's entire color balance is ~40 lines of C:

```c
// ASC CDL mode (what Resolve uses)
float colorbalance_cdl(float in, float offset, float power, float slope) {
    float x = in * slope + offset;
    CLAMP(x, 0.0f, 1.0f);
    return powf(x, power);
}

// Lift/Gamma/Gain mode  
float colorbalance_lgg(float in, float lift_lgg, float gamma_inv, float gain) {
    float x = (((linearrgb_to_srgb(in) - 1.0f) * lift_lgg) + 1.0f) * gain;
    if (x < 0.f) x = 0.f;
    return powf(srgb_to_linearrgb(x), gamma_inv);
}
```

And the GLSL shader (for GPU) is already written and ready to use directly.

---

## Architecture: How It All Fits

```
┌─────────────────────────────────────────────────────────────────┐
│                     YOUR CUSTOM UI (PySide6)                      │
│  ┌──────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │ Gallery  │  │   Viewer (OpenGL)    │  │  Node Graph      │  │
│  │ Stills   │  │                      │  │  ┌──┐ ┌──┐ ┌──┐ │  │
│  └──────────┘  └──────────────────────┘  │  │N1│→│N2│→│N3│ │  │
│                                           │  └──┘ └──┘ └──┘ │  │
│  ┌──────────────────────────────────────┐ └──────────────────┘  │
│  │       Color Wheels / Curves          │                        │
│  │  ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──────────┐  │  ┌──────────────────┐  │
│  │  │L │ │G │ │G │ │O │ │ Curves   │  │  │  Scopes          │  │
│  │  └──┘ └──┘ └──┘ └──┘ └──────────┘  │  │  Waveform, Vec,  │  │
│  └──────────────────────────────────────┘  │  Histogram, CIE  │  │
│                                            └──────────────────┘  │
├─────────────────── BLENDER ENGINE ──────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Color Math (ported from Blender C → Python numpy)         │ │
│  │  • colorbalance_cdl()   • colorbalance_lgg()               │ │
│  │  • rgb_to_hsv/hsl/yuv   • evaluate_curve()                 │ │
│  │  • apply_3d_lut()       • color_matte()                    │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  GLSL Shaders (copied directly from Blender source)         │ │
│  │  • gpu_shader_compositor_color_balance.glsl                 │ │
│  │  • gpu_shader_compositor_curves.glsl                        │ │
│  │  • gpu_shader_compositor_color_matte.glsl                   │ │
│  │  • gpu_shader_common_color_utils.glsl                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  OpenColorIO Config (same config Blender + Resolve use)    │ │
│  │  • ACES 1.3 / 2.0 pipeline                                 │ │
│  │  • Rec709, sRGB, P3, BT.2020 color spaces                  │ │
│  │  • ARRI LogC, Sony S-Log3, RED Log3G10, Canon Log          │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## What You Build vs What Blender Gives You

| Component | Source | Effort |
|---|---|---|
| Color wheel UI | **You build** (custom Qt widget) | 3 days |
| Curve canvas UI | **You build** (custom Qt widget) | 2 days |
| Viewer with zoom/pan | **You build** (QOpenGLWidget) | 2 days |
| Timeline strip | **You build** (QWidget) | 1 day |
| Scope rendering | **You build** (QOpenGLWidget) | 3 days |
| Node graph UI | **You build** (QGraphicsView) | 5 days |
| **Color math** (CDL, LGG) | **Blender code** → port 40 lines to Python | 1 hour |
| **GLSL shaders** | **Blender code** → copy directly | 1 hour |
| **Color space transforms** | **OpenColorIO** → use config file | 2 hours |
| **LUT parsing** | **Blender code** → port .cube parser | 2 hours |
| **Color conversions** (RGB↔HSV↔HSL) | **Blender code** → copy `gpu_shader_common_color_utils.glsl` | 30 min |
| **Keying/matte** | **Blender code** → port `color_matte` | 1 hour |

**Total new code you write:** ~5,000 lines of Python (UI)
**Total code you borrow from Blender:** ~200 lines of Python + 4 GLSL files

---

## Phase 1 — Core Color Math (port from Blender C → Python numpy)

Copy the exact math from Blender's source, translate to Python:

```
source/blender/nodes/composite/nodes/node_composite_color_balance.cc
  ↓
core/color_math.py  (40 lines of critical math)
```

```python
# From Blender's colorbalance_cdl() — exact ASC CDL spec
def colorbalance_cdl(in_val, offset, power, slope):
    x = in_val * slope + offset
    x = max(0.0, min(1.0, x))
    return pow(x, power)

# From Blender's colorbalance_lgg() — Lift/Gamma/Gain
def colorbalance_lgg(in_val, lift, gamma_inv, gain):
    x = ((srgb_to_linearrgb(in_val) - 1.0) * (2.0 - lift) + 1.0) * gain
    if x < 0.0: x = 0.0
    return linearrgb_to_srgb(pow(x, gamma_inv))
```

Also port these from Blender's `gpu_shader_common_color_utils.glsl`:
- `rgb_to_hsv`, `hsv_to_rgb`
- `rgb_to_hsl`, `hsl_to_rgb`
- `rgb_to_yuv_itu_709`, `yuv_to_rgb_itu_709`

## Phase 2 — GLSL Shaders (copy directly from Blender)

Copy these files from `blender/source/blender/compositor/shaders/library/`:

| Blender File | Our File | Purpose |
|---|---|---|
| `gpu_shader_compositor_color_balance.glsl` | `shaders/color_balance.glsl` | LGG + CDL + white point |
| `gpu_shader_compositor_curves.glsl` | `shaders/curves.glsl` | RGB + HSL curves |
| `gpu_shader_common_color_utils.glsl` | `shaders/color_utils.glsl` | RGB↔HSV↔HSL↔YUV |
| `gpu_shader_compositor_color_matte.glsl` | `shaders/color_matte.glsl` | Chroma/Luma key |
| `gpu_shader_compositor_blur.glsl` | `shaders/blur.glsl` | Gaussian blur |
| `gpu_shader_compositor_mix.glsl` | `shaders/mix.glsl` | 26 blend modes |

## Phase 3 — UI Framework (you build)

**Tech:** PySide6 (Qt6) via pip install

## Phase 4 — Color Management (OpenColorIO)

Blender + Resolve both use **OpenColorIO**.

---

## Why This Works on Your Low-End PC

| Concern | Mitigation |
|---|---|
| Intel HD 5500 iGPU | simple GLSL shaders run 60fps at 1080p |
| No GPU | numpy processes 1080p in ~5ms per op |
| Memory | 1080p = 8MB, cache 60 frames = 480MB |
| Python 3.14 | pure numpy + PySide6, no bpy needed |
| No Blender install | we only copy math/shader source files |
