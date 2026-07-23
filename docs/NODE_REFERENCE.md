# Node Reference

Complete reference for all 25 processing nodes in davici-resolve.

All nodes are ported from Blender's GPL compositor source code.

---

## Color Correction Nodes

### Color Balance LGG (Lift/Gamma/Gain)
- **Source**: `blender/compositor/shaders/library/gpu_shader_compositor_color_balance.glsl`
- **Parameters**:
  - `lift` — [R, G, B] shadow adjustment (default: [0, 0, 0])
  - `gamma` — [R, G, B] midtone adjustment (default: [1, 1, 1])
  - `gain` — [R, G, B] highlight adjustment (default: [1, 1, 1])
  - `offset` — [R, G, B] global offset (default: [0, 0, 0])
  - `factor` — Blend strength 0-1 (default: 1.0)

### Color Balance CDL (ASC CDL)
- **Source**: `blender/compositor/shaders/library/gpu_shader_compositor_color_balance.glsl`
- **Parameters**:
  - `slope` — [R, G, B] multiplicative (default: [1, 1, 1])
  - `offset` — [R, G, B] additive (default: [0, 0, 0])
  - `power` — [R, G, B] exponent (default: [1, 1, 1])
  - `factor` — Blend strength 0-1 (default: 1.0)
- **Formula**: `result = (input * slope + offset) ^ power`

### Brightness/Contrast
- **Parameters**:
  - `brightness` — -100 to +100 (default: 0)
  - `contrast` — -100 to +100 (default: 0)

### Exposure
- **Parameters**:
  - `exposure` — EV stops, -5.0 to +5.0 (default: 0)
- **Formula**: `result = input * 2^exposure`

### Hue/Saturation/Value
- **Parameters**:
  - `hue` — Hue rotation 0-1 (default: 0)
  - `saturation` — Saturation multiplier -1 to +1 (default: 0)
  - `value` — Value multiplier -1 to +1 (default: 0)
  - `factor` — Blend strength 0-1 (default: 1.0)

### Gamma
- **Parameters**:
  - `gamma` — Gamma value > 0 (default: 1.0)
- **Formula**: `result = input ^ (1/gamma)`

---

## Adjustments

### Invert
- **Parameters**:
  - `factor` — Invert strength 0-1 (default: 1.0)
  - `invert_color` — Invert RGB channels (default: True)
  - `invert_alpha` — Invert alpha channel (default: False)

### Posterize
- **Parameters**:
  - `steps` — Number of discrete levels 2-1024 (default: 32)

### Levels
- **Parameters**:
  - `channel` — 0=luminance, 1=R, 2=G, 3=B (default: 0)
  - `in_min` — Input black point 0-1 (default: 0)
  - `in_max` — Input white point 0-1 (default: 1)
  - `out_min` — Output black point 0-1 (default: 0)
  - `out_max` — Output white point 0-1 (default: 1)
  - `gamma` — Midtone gamma > 0 (default: 1.0)

### Shadows/Highlights
- **Parameters**:
  - `shadows` — Shadow strength -1 to +1 (default: 0)
  - `highlights` — Highlight strength -1 to +1 (default: 0)
  - `shadow_tone` — Shadow tonal range 0-1 (default: 0.5)
  - `highlight_tone` — Highlight tonal range 0-1 (default: 0.5)
  - `color_correction` — Saturation boost in shadows -1 to +1 (default: 0)

### Color Temperature
- **Parameters**:
  - `temperature` — White point in Kelvin 1667-25000 (default: 6500)
  - `tint` — Green/magenta shift (default: 0)
- Uses Bradford chromatic adaptation from Blender source

### Split Toning
- **Parameters**:
  - `shadow_color` — (R, G, B) shadow tint (default: [0.5, 0.5, 0.6])
  - `highlight_color` — (R, G, B) highlight tint (default: [0.6, 0.5, 0.4])
  - `balance` — Shadow/highlight balance -1 to +1 (default: 0)
  - `factor` — Blend strength 0-1 (default: 1.0)

---

## Effects

### Vignette
- **Parameters**:
  - `strength` — Darkening amount 0-1 (default: 0.5)
  - `size` — Inner radius 0-1 (default: 0.8)
  - `feather` — Soft edge width 0-1 (default: 0.4)
  - `center_x` — Horizontal center 0-1 (default: 0.5)
  - `center_y` — Vertical center 0-1 (default: 0.5)

### Film Grain
- **Parameters**:
  - `amount` — Grain intensity 0-1 (default: 0.1)
  - `size` — Grain size multiplier (default: 1.0)
  - `seed` — Random seed (default: 0)

### Gaussian Blur
- **Parameters**:
  - `size` — Kernel size in pixels, odd number (default: 5)
  - `sigma` — Blur radius (default: 1.0)
- Uses pure NumPy 2D convolution

### Glow / Bloom
- **Parameters**:
  - `threshold` — Brightness threshold 0-1 (default: 0.8)
  - `softness` — Glow spread 0-1 (default: 0.5)
  - `intensity` — Glow brightness 0-1 (default: 0.5)
  - `size` — Blur kernel size (default: 21)

### Sharpen (Unsharp Mask)
- **Parameters**:
  - `amount` — Sharpening strength (default: 1.0)
  - `radius` — Blur radius (default: 1.0)
  - `threshold` — Detail threshold 0-1 (default: 0.0)

---

## Compositing

### Alpha Over
- **Parameters**:
  - `premul` — Use premultiplied alpha (default: True)
  - `factor` — Blend factor 0-1 (default: 1.0)

### Pixelate
- **Parameters**:
  - `size` — Block size in pixels (default: 10)

### Tonemap (Reinhard)
- **Parameters**:
  - `key` — Middle gray key value (default: 0.18)
  - `offset` — Brightness offset (default: 0)
  - `gamma` — Output gamma (default: 1.0)

### Blend (20 Modes)
- **Parameters**:
  - `mode` — Blend mode name (default: 'mix')
  - `fac` — Blend factor 0-1 (default: 0.5)
- **Modes**: mix, add, subtract, multiply, screen, darken, lighten, difference, divide, hard light, soft light, dodge, burn, exclusion, linear burn, overlay, color dodge, color burn, vivid light, pin light

---

## Keying (7 Types)

### Keying
- Full chroma key with despill
- **Parameters**: `key_color`, `balance`, `black_level`, `white_level`, `despill_strength`, `despill_balance`

### Color Key
- Key by RGB distance from a target color

### Chroma Key
- Key by hue angle range

### Difference Key
- Key by difference from a background image

### Luminance Key
- Key by brightness range

### Channel Key
- Key by a specific channel value

### Distance Key
- Key by color distance in YCbCr space

---

## Color Space Conversion

### Node: Convert Colorspace
- Convert between sRGB, Linear, HSV, HSL, YUV, YCbCr
- Uses Blender's color space definitions

### Node: Combine/Separate Color
- Combine or separate RGB, HSV, HSL, YUV channels

---

## Running Nodes in Code

```python
from nodes import create_node, NODE_CLASSES

# Create a node
node = create_node("color_balance_lgg", "My Balance")

# Set parameters
node.params['gain'] = [1.2, 1.0, 0.8]

# Process an image
import numpy as np
image = np.random.rand(100, 100, 3).astype(np.float32)
result = node.process({"Image": image})

# List all available nodes
print(list(NODE_CLASSES.keys()))
```
