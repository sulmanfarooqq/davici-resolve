# Palette Reference — Complete DaVinci Resolve Color Page Breakdown

This document catalogs every palette, panel, and tool in DaVinci Resolve's Color Page
with exact parameter names, ranges, defaults, and behaviors.

---

## LEFT PALETTES (6)

### 1. Camera Raw Palette
Controls for decoding raw camera media. Palette changes based on camera type.

**Common controls:**
| Parameter | Range | Default | Description |
|---|---|---|---|
| White Balance | 2000–50000K | as-shot | Color temperature |
| Tint | -100–100 | 0 | Green/magenta correction |
| ISO | 100–25600 | as-shot | Sensor sensitivity |
| Exposure | -5–5 EV | 0 | Brightness adjustment |
| Color Science | — | camera default | ARRI, RED, Sony, Canon, etc. specific |
| Sharpness | 0–100 | 50 | Detail enhancement |
| Highlight Recovery | 0–100 | 0 | Recover blown highlights |
| Shadow Recovery | 0–100 | 0 | Lift shadow detail |

**Per-camera tabs:** ARRI Alexa, RED, Sony Venice, Canon Cinema RAW, Blackmagic RAW,
Panasonic Varicam, etc.

### 2. Color Match Palette
Auto-matching and color balance tools.

| Tool | Description |
|---|---|
| Auto Color | One-click balance: adjusts color and contrast automatically |
| Auto White Balance | Sets white point based on brightest pixel |
| Shot Match | Match current clip to reference clip's color/contrast/brightness |
| Color Chart Match | Match to X-Rite/DSC/Datacolor chart: align grid on frame → auto-match |
| Match Type | Hue Match, Luma Match, Full Match |

### 3. Primaries Palette (Color Wheels)
The most used palette. 4 views in one panel.

#### 3a. Color Wheels View
| Wheel | Tonal Range | Master Slider (Y) | Purpose |
|---|---|---|---|
| Lift | Shadows | -1.0–1.0 | Black point & shadow color |
| Gamma | Midtones | -1.0–1.0 | Midtone brightness & color |
| Gain | Highlights | -1.0–1.0 | White point & highlight color |
| Offset | All | -1.0–1.0 | Global brightness shift |

Color balance: drag puck in circle. X/Y mapped to R-B and G-M axes. Range: -1 to 1 per axis.

#### 3b. Primary Bars View
| Bar | Channel | Range |
|---|---|---|
| Master (Y) | Luminance | -1.0–1.0 |
| Red | R channel | -1.0–1.0 |
| Green | G channel | -1.0–1.0 |
| Blue | B channel | -1.0–1.0 |

#### 3c. Log Wheels View
| Wheel | Tonal Range | Description |
|---|---|---|
| Shadow | Low end of log curve | More precise than Lift |
| Midtone | Middle of log curve | More precise than Gamma |
| Highlight | High end of log curve | More precise than Gain |

#### 3d. Adjustment Controls
| Control | Range | Default | Description |
|---|---|---|---|
| Contrast | -1.0–1.0 | 0 | S-curve contrast (centered at pivot) |
| Pivot | 0.0–1.0 | 0.435 | Contrast center point |
| Saturation | -1.0–1.0 | 0 | Global color intensity |
| Hue | -1.0–1.0 | 0 | Global hue rotation |
| Temperature | -1.0–1.0 | 0 | Blue→orange warmth |
| Tint | -1.0–1.0 | 0 | Green→magenta correction |
| Midtone Detail | -1.0–1.0 | 0 | Edge contrast in midtones (clarity) |
| Color Boost | -1.0–1.0 | 0 | Vibrance: intelligently saturates unsaturated areas |
| Shadows | -1.0–1.0 | 0 | Lift shadow brightness |
| Highlights | -1.0–1.0 | 0 | Reduce/increase highlight brightness |

### 4. HDR Palette
Zone-based grading for wide gamut/HDR content.

| Zone | Range | Description |
|---|---|---|
| Custom zones | User-defined | Create wheels for arbitrary tonal ranges |
| Super Blacks | Below black | Recover crushed shadows |
| Shadows | 0–25% | Dark tones |
| Midtones | 25–75% | Mid-range |
| Highlights | 75–100% | Bright tones |
| Specular Highlights | Above 100% | Super-white detail |
| **Global controls** | | |
| Exposure | -5–5 EV | Overall exposure |
| Gamma | 0.1–5.0 | Display gamma |
| Highlight Recovery | 0–100 | HDR highlight reconstruction |

Dolby Vision CM 4.0 metadata: L1/L2/L3 trim passes, HDR10+ dynamic metadata.

### 5. RGB Mixer Palette
| Mixer | Output R | Output G | Output B | Range |
|---|---|---|---|---|
| Input Red → | 0–200% | 0–200% | 0–200% | Default R:R=100% |
| Input Green → | 0–200% | 0–200% | 0–200% | Default G:G=100% |
| Input Blue → | 0–200% | 0–200% | 0–200% | Default B:B=100% |
| Monochrome | — | — | — | Luminance-only output |
| Presets | Rec709→P3, B&W, etc.

### 6. Motion Effects Palette
| Control | Range | Description |
|---|---|---|
| Motion Blur | 0–100 | Artificial motion blur via optical flow |
| Flicker Reduction | 0–100 | Anti-flicker for interviews |
| Frame Blend | — | Blend frames for slow-motion |
| Optical Flow | — | Frame interpolation mode (better/smoother/faster) |

---

## CENTRAL PALETTES (11)

### 7. Curves Palette
**Custom Curves:**
| Curve | Channels | Use |
|---|---|---|
| Luma | Y | Luminance contrast |
| Red | R | Red channel curve |
| Green | G | Green channel curve |
| Blue | B | Blue channel curve |

**HSL Curves (6):**
| Curve | X-Axis | Y-Axis | Use |
|---|---|---|---|
| Hue vs Hue | Input Hue | Output Hue shift | Change any hue to another hue |
| Hue vs Sat | Input Hue | Saturation multiplier | Boost/reduce saturation per hue |
| Hue vs Lum | Input Hue | Luminance multiplier | Lighten/darken per hue |
| Lum vs Sat | Input Luma | Saturation multiplier | Adjust saturation by brightness |
| Sat vs Sat | Input Saturation | Saturation multiplier | Adjust saturation by saturation level |
| Sat vs Lum | Input Saturation | Luminance multiplier | Adjust brightness by saturation |

Each curve: draggable control points, spline interpolation, histogram background.

### 8. ColorSlice Palette
6-vector color wheels. Each vector has 3 controls:
| Vector | Hue | Saturation | Luminance |
|---|---|---|---|
| Red | -180°–180° | -100–100% | -100–100% |
| Green | -180°–180° | -100–100% | -100–100% |
| Blue | -180°–180° | -100–100% | -100–100% |
| Cyan | -180°–180° | -100–100% | -100–100% |
| Magenta | -180°–180° | -100–100% | -100–100% |
| Yellow | -180°–180° | -100–100% | -100–100% |

### 9. Color Warper Palette
2D grid overlay in polar color space (hue = angle, saturation = radius).
- Drag grid points to warp color mapping
- Grid sizes: 6×4, 12×8, 24×16
- Picker: click on viewer image to see its position on grid
- Softness control for transition smoothness

### 10. Qualifier Palette
**Selection:**
| Tool | Description |
|---|---|
| Eyedropper | Click+drag on viewer to sample range |
| Hue range | H gradient bar with adjustable handles |
| Saturation range | S gradient bar with adjustable handles |
| Luminance range | L gradient bar with adjustable handles |
| 3D preview | Shows selected region in viewer overlay |
| Magic Wand | View key (alpha matte) in viewer |
| Highlight | Display selected area highlighted |

**Range controls per channel (H/S/L):**
| Control | Range | Description |
|---|---|---|
| Min | 0.0–1.0 | Low bound |
| Max | 0.0–1.0 | High bound |
| Low Softness | 0.0–1.0 | Falloff at low bound |
| High Softness | 0.0–1.0 | Falloff at high bound |

**Matte Finesse:**
| Control | Range | Default | Description |
|---|---|---|---|
| Clean Black | 0.0–1.0 | 0.0 | Clip low alpha values |
| Clean White | 0.0–1.0 | 0.0 | Clip high alpha values |
| Blur Radius | 0–100 | 0 | Gaussian blur on matte |
| Erode | -100–100 | 0 | Shrink/grow matte |
| Dilate | -100–100 | 0 | Expand matte |
| Highlight Rolloff | 0–100 | 0 | Smooth bright transition |
| Shadow Rolloff | 0–100 | 0 | Smooth dark transition |

### 11. Window Palette (Power Windows)
| Shape | Icon | Controls |
|---|---|---|
| Circle | ● | Center X/Y, Radius, Aspect, Feather, Rotation |
| Rectangle | ▬ | Center X/Y, Width, Height, Feather, Rotation, Corner Rounding |
| Polygon | ⬠ | N control points, Feather, Rotation |
| Curve (Bezier) | ⤴ | Control points with bezier handles, Feather |
| Gradient | ▨ | Start/End point, Angle, Softness |

**All shapes:** Invert toggle, Inside/Outside mode, Softness control

**On-screen controls (in viewer):**
- Drag shape → move
- Drag edge handles → resize (proportional with Shift)
- Drag corner → rotate
- Drag circle handle → feather
- Double-click edge → add point (polygon/curve)

### 12. Tracker Palette
| Control | Description |
|---|---|
| Track Forward | Analyze from playhead forward |
| Track Reverse | Analyze from playhead backward |
| Track All | Analyze entire clip from start |
| Reset | Clear all tracking data |
| **Track Mode** | |
| Pan | Horizontal motion |
| Tilt | Vertical motion |
| Zoom | Scale change |
| Rotation | Angular change |
| Perspective | 3D perspective change |
| **Keyframe list** | Table of tracked positions per frame |
| Curves | Bezier interpolation of track path |
| Stabilization | Use tracker data to stabilize image |
| Lock | Prevent tracker from updating (manual keyframe) |

### 13. Magic Mask Palette (Studio)
| Control | Description |
|---|---|
| People | Auto-detect human body/face/skin |
| Objects | Auto-detect objects in frame |
| Track | Analyze object through clip |
| Refine Edge | Improve mask edge quality |
| Show Overlay | RGBA mask preview |

### 14. Blur Palette
| Type | Controls |
|---|---|
| Gaussian Blur | Radius X/Y (1–100), Linked toggle |
| Directional Blur | Angle, Length |
| Motion Blur | Angle, Length, Softness |
| Radial Blur | Center X/Y, Amount |

### 15. Key Palette
Matte post-processing applied after qualifier/window.
| Control | Range | Default |
|---|---|---|
| Erode Horizontal | -100–100 | 0 |
| Erode Vertical | -100–100 | 0 |
| Dilate Horizontal | -100–100 | 0 |
| Dilate Vertical | -100–100 | 0 |
| Blur Horizontal | 0–100 | 0 |
| Blur Vertical | 0–100 | 0 |
| Softness | 0–100 | 0 |
| Highlight Rolloff | 0–100 | 0 |
| Shadow Rolloff | 0–100 | 0 |
| Invert | 0/1 | 0 |

### 16. Sizing Palette
| Control | Range | Description |
|---|---|---|
| Pan X | -inf–inf | Horizontal position |
| Pan Y | -inf–inf | Vertical position |
| Tilt | -inf–inf | Vertical offset |
| Zoom X | 0.1–10.0 | Horizontal scale |
| Zoom Y | 0.1–10.0 | Vertical scale |
| Zoom Linked | 0/1 | Lock X/Y together |
| Rotate | -180–180 | Rotation angle |
| Flip Horizontal | 0/1 | Mirror X |
| Flip Vertical | 0/1 | Mirror Y |
| Input Sizing | — | Size the source |
| Output Sizing | — | Size the output |

### 17. Stereoscopic 3D Palette
| Control | Description |
|---|---|
| Convergence | Left/eye offset for 3D |
| Left Eye | Left eye controls |
| Right Eye | Right eye controls |
| Swap Eyes | Swap left/right |
| Depth Map | 3D depth visualization |

---

## SUPPLEMENTARY PANELS

### Open FX Panel (Top-Right)
Effects categorized as:
| Category | Examples |
|---|---|
| Blur | Gaussian, Directional, Motion, Radial, Lens Blur |
| Color Effects | Color Compressor, Color Space Transform, Gamma, Hue vs Hue, Tint, Sepia, etc. |
| Glow | Glow, Halation, Lens Flare, Light Rays |
| Image | Brightness/Contrast, Hue/Saturation, Levels, Shadows/Highlights |
| Key | Chroma Key, HSV Key, Luma Key |
| Noise Reduction | Spatial NR, Temporal NR, Motion NR |
| Object Removal | Patch Remover, Object Remover |
| Open FX | 3rd-party plugins (OFX standard) |
| Refine | Beauty, Face Refinement, Skin Smoothing, Eye Enhance |
| Resolve FX | Color Shift, Edge Detection, Film Grain, Fog, Glow, Halation, Mist, Night, Old Film, etc. |
| Restoration | Dead Pixel Fixer, Dust Busting, Line Scratch Removal, Fix Frame |
| Sharpen | Sharpen, Unsharp Mask |
| Stylize | CRT, Dither, Mosaic, Posterize, Solarize |
| Texture | Add Texture, Emboss, Etch |
| Time | Motion Blur, Speed Change |
| Transform | Corner Pin, Crop, Resize, Rotate, Transform |
| Warp | Warp, Mesh Warp, Perspective, Spherize, Twirl |

### Gallery (Top-Left)
| Feature | Description |
|---|---|
| Grab Still | Capture current frame + grade |
| Albums | Organize stills into groups |
| Apply Grade | Copy grade from still to current clip |
| Export Still | Save as image + .drx grade file |
| Import Still | Load .drx grade into gallery |
| Delete | Remove still |
| Compare | Use still as reference for wipe |

### LUT Browser (Top-Left)
| Feature | Description |
|---|---|
| Folder tree | Organized by category |
| Preview | Hover to temporarily apply |
| Apply | Drag to node or right-click node → LUT |
| 1D LUTs | .cube, .spi1d |
| 3D LUTs | .cube, .spi3d, .look |
| Import | Add LUTs from file system |

### Scopes (Bottom-Right)
| Scope | Modes | Description |
|---|---|---|
| Waveform | RGB, YRGB, YCbCr, Y | Overlaid luma/chroma vs position |
| Parade | RGB, YRGB, YCbCr | Side-by-side channel signals |
| Vectorscope | 100%, 75% | Polar chroma plot with skin tone line |
| Histogram | RGB, Y, Luma | Value distribution with shadow/midtone/highlight zones |
| CIE Chromaticity | 1931 xy, 1976 u'v' | Gamut triangle, BT.2020/P3/Rec709 overlays |

**Scope settings per type:**
- Waveform: Opacity (1–100), Grid (On/Off)
- Vectorscope: Skin Tone Indicator (On/Off), Colorize (On/Off)
- Histogram: Log Scale (On/Off), Channels (RGB/Y)
- CIE: Gamut (Rec709/P3/BT2020), White Point

### Keyframe Editor (Bottom-Right)
| Feature | Description |
|---|---|
| Keyframe list | All animated parameters |
| Timeline | Frame-by-frame navigation |
| Curve editor | Bezier interpolation for each keyframe |
| Copy/Paste | Keyframe operations |
| Linear/Smooth/Step | Interpolation modes |
| Previous/Next | Jump between keyframes |

### Info Panel (Bottom-Right)
| Field | Description |
|---|---|
| Name | Clip filename |
| Type | Video format |
| Resolution | Width × Height |
| Frame Rate | fps |
| Duration | Timecode |
| Codec | Video codec name |
| Data Level | Video/Full |
| Color Space | Color primaries |
| Gamma | Transfer function |
