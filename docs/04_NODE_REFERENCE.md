# Node Reference

## Architecture

The node graph is a **Directed Acyclic Graph (DAG)** where each node is an independent
processing step. The image flows from input (left) to output (right), passing through
each connected node.

### Base Node Interface

```python
class BaseNode:
    type: str          # Node type identifier
    id: str            # UUID
    label: str         # User-defined name
    color: str         # Hex color label
    inputs: List[Socket]
    outputs: List[Socket]
    params: Dict       # Node-specific parameters
    bypass: bool
    solo: bool
    enabled: bool
    dirty: bool
    cached_output: np.ndarray | None

    def process(self, frame: np.ndarray) -> np.ndarray
    def get_param(self, key: str) -> Any
    def set_param(self, key: str, value: Any) -> None
    def mark_dirty(self) -> None
    def to_dict() -> dict
    def from_dict(data: dict) -> BaseNode
```

---

## Complete Node Catalog

### 1. Color Wheel Node
**Type:** `color_wheel`
**Inputs:** 1 (RGB)  **Outputs:** 1 (RGB)
**Palette:** Primaries → Wheels

| Param | Type | Range | Default | Description |
|---|---|---|---|---|
| `lift` | vec3 | [-1, 1] | [0,0,0] | Shadow color offset |
| `gamma` | vec3 | [0.01, 5] | [1,1,1] | Midtone power |
| `gain` | vec3 | [0, 10] | [1,1,1] | Highlight multiplier |
| `offset` | vec3 | [-1, 1] | [0,0,0] | Global offset |
| `pivot` | float | [0, 1] | 0.435 | Contrast center |
| `contrast` | float | [-1, 1] | 0 | S-curve amount |
| `saturation` | float | [-1, 1] | 0 | Global saturation |
| `hue` | float | [-1, 1] | 0 | Hue rotation |
| `temp` | float | [-1, 1] | 0 | Temperature (blue↔orange) |
| `tint` | float | [-1, 1] | 0 | Tint (green↔magenta) |
| `color_boost` | float | [-1, 1] | 0 | Vibrance |
| `midtone_detail` | float | [-1, 1] | 0 | Clarity/sharpness |
| `shadows` | float | [-1, 1] | 0 | Shadow lift |
| `highlights` | float | [-1, 1] | 0 | Highlight gain |

### 2. Primary Bars Node
**Type:** `primary_bars`
**Inputs:** 1 (RGB)  **Outputs:** 1 (RGB)
**Palette:** Primaries → Bars

| Param | Type | Range | Default |
|---|---|---|---|
| `master` | float | [-1, 1] | 0 |
| `red` | float | [-1, 1] | 0 |
| `green` | float | [-1, 1] | 0 |
| `blue` | float | [-1, 1] | 0 |

### 3. Log Wheels Node
**Type:** `log_wheels`
**Inputs:** 1 (RGB)  **Outputs:** 1 (RGB)
**Palette:** Primaries → Log

| Param | Type | Range | Default |
|---|---|---|---|
| `shadow` | vec3 | [-1, 1] | [0,0,0] |
| `midtone` | vec3 | [-1, 1] | [0,0,0] |
| `highlight` | vec3 | [-1, 1] | [0,0,0] |

### 4. Curves Node
**Type:** `curves`
**Inputs:** 1 (RGB)  **Outputs:** 1 (RGB)
**Palette:** Curves

| Param | Type | Range | Description |
|---|---|---|---|
| `luma` | point[] | [(0,0)...(1,1)] | Luma curve points |
| `red` | point[] | [(0,0)...(1,1)] | Red channel curve |
| `green` | point[] | [(0,0)...(1,1)] | Green channel curve |
| `blue` | point[] | [(0,0)...(1,1)] | Blue channel curve |
| `hue_vs_hue` | point[] | [(0,0)...(1,0)] | Hue→hue shift |
| `hue_vs_sat` | point[] | [(0,0)...(1,0)] | Hue→sat multiplier |
| `hue_vs_lum` | point[] | [(0,0)...(1,0)] | Hue→lum multiplier |
| `lum_vs_sat` | point[] | [(0,0)...(1,0)] | Luma→sat multiplier |
| `sat_vs_sat` | point[] | [(0,0)...(1,1)] | Sat→sat multiplier |
| `sat_vs_lum` | point[] | [(0,0)...(1,0)] | Sat→lum multiplier |
| `active_curve` | int | 0–9 | Which curve is being edited |

Each point: `(x: float, y: float)` normalized to [0, 1].

### 5. Color Slice Node
**Type:** `color_slice`
**Inputs:** 1 (RGB)  **Outputs:** 1 (RGB)
**Palette:** ColorSlice

| Param | Type | Range | Default |
|---|---|---|---|
| `red_hue` | float | [-180, 180] | 0 |
| `red_sat` | float | [-100, 100] | 0 |
| `red_lum` | float | [-100, 100] | 0 |
| `green_hue` | float | [-180, 180] | 0 |
| `green_sat` | float | [-100, 100] | 0 |
| `green_lum` | float | [-100, 100] | 0 |
| `blue_hue` | float | [-180, 180] | 0 |
| `blue_sat` | float | [-100, 100] | 0 |
| `blue_lum` | float | [-100, 100] | 0 |
| `cyan_hue` | float | [-180, 180] | 0 |
| `cyan_sat` | float | [-100, 100] | 0 |
| `cyan_lum` | float | [-100, 100] | 0 |
| `magenta_hue` | float | [-180, 180] | 0 |
| `magenta_sat` | float | [-100, 100] | 0 |
| `magenta_lum` | float | [-100, 100] | 0 |
| `yellow_hue` | float | [-180, 180] | 0 |
| `yellow_sat` | float | [-100, 100] | 0 |
| `yellow_lum` | float | [-100, 100] | 0 |

### 6. Color Warper Node
**Type:** `color_warper`
**Inputs:** 1 (RGB)  **Outputs:** 1 (RGB)
**Palette:** Color Warper

| Param | Type | Range | Default |
|---|---|---|---|
| `grid_size` | int | 6/12/24 | 12 |
| `grid_points` | float[] | [-1,1] | zeros |
| `softness` | float | [0, 100] | 50 |
| `picker_enabled` | bool | — | False |

Grid points: 2D deformation grid in hue-saturation space.

### 7. CST Node (Color Space Transform)
**Type:** `cst`
**Inputs:** 1 (RGB)  **Outputs:** 1 (RGB)
**Palette:** (via Resolve FX or built-in)

| Param | Type | Options | Description |
|---|---|---|---|
| `input_cs` | str | Rec709, sRGB, P3D65, ACEScg, ACEScc, LogC, SLog3, VLog, etc. | Source color space |
| `output_cs` | str | same list | Target color space |
| `input_gamma` | str | Linear, sRGB, Rec709, BT1886, PQ, HLG, LogC, SLog3, etc. | Source gamma |
| `output_gamma` | str | same list | Target gamma |
| `tone_map` | bool | — | Apply tone mapping for HDR→SDR |
| `method` | str | matrix, log, log_inv | Transform method |

### 8. LUT Node
**Type:** `lut`
**Inputs:** 1 (RGB)  **Outputs:** 1 (RGB)
**Palette:** LUT Browser (drag)

| Param | Type | Range | Default |
|---|---|---|---|
| `path` | str | — | "" |
| `interpolation` | str | trilinear, tetrahedral | trilinear |
| `mix` | float | [0, 1] | 1.0 |
| `pre_contrast` | float | [-1, 1] | 0 |
| `pre_saturation` | float | [-1, 1] | 0 |
| `post_contrast` | float | [-1, 1] | 0 |
| `post_saturation` | float | [-1, 1] | 0 |

### 9. Qualifier Node
**Type:** `qualifier`
**Inputs:** 1 (RGB)  **Outputs:** 1 (RGB + Alpha)
**Palette:** Qualifier

| Param | Type | Range | Default |
|---|---|---|---|
| `hue_min` | float | [0, 1] | 0 |
| `hue_max` | float | [0, 1] | 1 |
| `hue_soft_low` | float | [0, 1] | 0 |
| `hue_soft_high` | float | [0, 1] | 0 |
| `sat_min` | float | [0, 1] | 0 |
| `sat_max` | float | [0, 1] | 1 |
| `sat_soft_low` | float | [0, 1] | 0 |
| `sat_soft_high` | float | [0, 1] | 0 |
| `lum_min` | float | [0, 1] | 0 |
| `lum_max` | float | [0, 1] | 1 |
| `lum_soft_low` | float | [0, 1] | 0 |
| `lum_soft_high` | float | [0, 1] | 0 |
| `clean_black` | float | [0, 1] | 0 |
| `clean_white` | float | [0, 1] | 0 |
| `blur_radius` | float | [0, 100] | 0 |
| `erode` | float | [-100, 100] | 0 |
| `dilate` | float | [-100, 100] | 0 |
| `highlight_rolloff` | float | [0, 100] | 0 |
| `shadow_rolloff` | float | [0, 100] | 0 |

### 10. Power Window Node
**Type:** `power_window`
**Inputs:** 1 (RGB)  **Outputs:** 1 (RGB + Alpha)
**Palette:** Window

| Param | Type | Range | Default |
|---|---|---|---|
| `shape` | str | circle, rectangle, polygon, curve, gradient | circle |
| `center_x` | float | [0, 1] | 0.5 |
| `center_y` | float | [0, 1] | 0.5 |
| `width` | float | [0, 1] | 0.5 |
| `height` | float | [0, 1] | 0.5 |
| `rotation` | float | [-180, 180] | 0 |
| `feather` | float | [0, 1] | 0.1 |
| `invert` | bool | — | False |
| `inside_outside` | int | 0=inside, 1=outside | 0 |
| `corner_radius` | float | [0, 1] | 0 |
| `points` | point[] | — | [] |
| `gradient_angle` | float | [0, 360] | 0 |

### 11. Blur Node
**Type:** `blur`
**Inputs:** 1 (RGB)  **Outputs:** 1 (RGB)
**Palette:** Blur

| Param | Type | Range | Default |
|---|---|---|---|
| `type` | str | gaussian, directional, motion, radial | gaussian |
| `radius_x` | float | [0, 100] | 0 |
| `radius_y` | float | [0, 100] | 0 |
| `linked` | bool | — | True |
| `angle` | float | [0, 360] | 0 |
| `center_x` | float | [0, 1] | 0.5 |
| `center_y` | float | [0, 1] | 0.5 |

### 12. Key Node (Matte Post-Process)
**Type:** `key`
**Inputs:** 1 (RGB + Alpha)  **Outputs:** 1 (RGB + Alpha)
**Palette:** Key

| Param | Type | Range | Default |
|---|---|---|---|
| `erode_h` | float | [-100, 100] | 0 |
| `erode_v` | float | [-100, 100] | 0 |
| `dilate_h` | float | [-100, 100] | 0 |
| `dilate_v` | float | [-100, 100] | 0 |
| `blur_h` | float | [0, 100] | 0 |
| `blur_v` | float | [0, 100] | 0 |
| `softness` | float | [0, 100] | 0 |
| `highlight_rolloff` | float | [0, 100] | 0 |
| `shadow_rolloff` | float | [0, 100] | 0 |
| `invert` | bool | — | False |

### 13. Sizing Node
**Type:** `sizing`
**Inputs:** 1 (RGB)  **Outputs:** 1 (RGB)
**Palette:** Sizing

| Param | Type | Range | Default |
|---|---|---|---|
| `pan_x` | float | [-inf, inf] | 0 |
| `pan_y` | float | [-inf, inf] | 0 |
| `zoom_x` | float | [0.1, 10] | 1.0 |
| `zoom_y` | float | [0.1, 10] | 1.0 |
| `zoom_linked` | bool | — | True |
| `rotate` | float | [-180, 180] | 0 |
| `flip_h` | bool | — | False |
| `flip_v` | bool | — | False |

### 14. Parallel Node
**Type:** `parallel`
**Inputs:** 2–N (RGB)  **Outputs:** 1 (RGB)

| Param | Type | Range | Default |
|---|---|---|---|
| `mix` | float[] | [0, 1] | equal weights |

Blends N inputs using weighted sum:
```
output = sum(input[i] * mix[i]) / sum(mix)
```

### 15. Layer Node
**Type:** `layer`
**Inputs:** 2 (bg: RGB, fg: RGB+Alpha)  **Outputs:** 1 (RGB)

| Param | Type | Range | Default |
|---|---|---|---|
| `composite_mode` | str | over, screen, multiply, overlay, difference, etc. | over |
| `fg_opacity` | float | [0, 1] | 1.0 |

### 16. Splitter / Combiner Nodes
**Type:** `splitter`
**Inputs:** 1 (RGB or YUV)  **Outputs:** 3 (R, G, B or Y, U, V)

**Type:** `combiner`
**Inputs:** 3 (R, G, B or Y, U, V)  **Outputs:** 1 (RGB)
