# Color Science Reference

## Primary Correction Model

### Lift/Gamma/Gain/Offset (Standard)

```
Output = ((Input + Lift) × Gain) ^ (1 / Gamma) + Offset
```

| Term | Range | Effect |
|---|---|---|
| Lift | [-1.0, 1.0] | Additive offset before gain (affects shadows more) |
| Gamma | (0.0, ∞)  | Power function exponent (1.0 = linear) |
| Gain | [0.0, ∞)  | Multiplicative scale (1.0 = no change) |
| Offset | [-1.0, 1.0] | Additive offset after gamma (affects all equally) |

### With Contrast and Pivot

```
c = rgb - pivot
rgb = rgb + c * contrast
rgb = ((rgb + lift) * gain) ^ (1/gamma) + offset
```

### With Saturation

```
luma = dot(rgb, vec3(0.2126, 0.7152, 0.0722))
rgb = mix(vec3(luma), rgb, 1.0 + saturation)
```

### Log Wheels (Shadow/Mid/Highlight)
Operate in log color space. Apply offset at three different luminance bands with
Gaussian falloff blending between bands:

```
shadow_weight = gaussian(luma, shadow_pivot, shadow_width)
mid_weight    = gaussian(luma, mid_pivot, mid_width)
highlight_weight = gaussian(luma, highlight_pivot, highlight_width)
rgb += shadow_offset * shadow_weight + mid_offset * mid_weight + highlight_offset * highlight_weight
```

---

## Curve Model

### Custom Curves
Points defined as (x, y) pairs normalized to [0, 1]. Interpolation:

1. **Catmull-Rom spline** (default): smooth through all points
2. **Linear**: straight lines between points
3. **Flat extrapolation**: y = first/last point outside range

Built into a 256-entry lookup table per curve/channel.

### HSL Curves
| Curve | Mapping |
|---|---|
| Hue vs Hue | hue_in → hue_shift (additive) |
| Hue vs Sat | hue_in → sat_multiplier (multiplicative) |
| Hue vs Lum | hue_in → lum_multiplier |
| Lum vs Sat | luma_in → sat_multiplier |
| Sat vs Sat | sat_in → sat_multiplier |
| Sat vs Lum | sat_in → lum_multiplier |

---

## Color Spaces

### Standard Color Primaries (CIE 1931 xy)

| Color Space | R_x | R_y | G_x | G_y | B_x | B_y | W_x | W_y |
|---|---|---|---|---|---|---|---|---|
| Rec.709 / sRGB | 0.640 | 0.330 | 0.300 | 0.600 | 0.150 | 0.060 | 0.3127 | 0.3290 |
| DCI-P3 | 0.680 | 0.320 | 0.265 | 0.690 | 0.150 | 0.060 | 0.3140 | 0.3510 |
| Display P3 | 0.680 | 0.320 | 0.265 | 0.690 | 0.150 | 0.060 | 0.3127 | 0.3290 |
| ACES AP0 | 0.7347 | 0.2653 | 0.0000 | 1.0000 | 0.0001 | -0.0770 | 0.32168 | 0.33767 |
| ACES AP1 | 0.713 | 0.293 | 0.165 | 0.830 | 0.128 | 0.044 | 0.32168 | 0.33767 |
| ARRI Wide Gamut | 0.6840 | 0.3130 | 0.2210 | 0.8480 | 0.0861 | -0.1020 | 0.3127 | 0.3290 |
| Sony S-Gamut3 | 0.730 | 0.280 | 0.160 | 0.830 | 0.100 | -0.040 | 0.3127 | 0.3290 |
| RED WCG | 0.680 | 0.320 | 0.265 | 0.690 | 0.150 | 0.060 | 0.3127 | 0.3290 |
| V-Gamut | 0.730 | 0.280 | 0.165 | 0.830 | 0.100 | -0.040 | 0.3127 | 0.3290 |
| Canon Cinema Gamut | 0.740 | 0.270 | 0.170 | 0.970 | 0.080 | -0.100 | 0.3127 | 0.3290 |
| BT.2020 | 0.708 | 0.292 | 0.170 | 0.797 | 0.131 | 0.046 | 0.3127 | 0.3290 |

### Transfer Functions

| Name | Type | Formula |
|---|---|---|
| Linear | Linear | `out = in` |
| sRGB | Gamma + linear segment | `out = 12.92*in` for `in≤0.0031308`, else `out = 1.055*in^(1/2.4) - 0.055` |
| Rec.709 | Gamma | `out = 4.5*in` for `in≤0.018`, else `out = 1.099*in^0.45 - 0.099` |
| BT.1886 | Gamma 2.4 | `out = in^(1/2.4)` |
| Gamma 2.2 | Pure gamma | `out = in^0.4545` |
| Gamma 2.6 | Pure gamma | `out = in^0.3846` |
| ST.2084 (PQ) | Perceptual Quantizer | See SMPTE ST.2084 (HDR) |
| HLG | Hybrid Log-Gamma | See ARIB STD-B67 (HDR) |
| ARRI LogC3 | Log | `out = (c*log10(a*in + b) + d)` for `in>cut`, else linear segment |
| Sony S-Log3 | Log | `out = (c*log10(in + b) + d)` for `in>cut`, else linear segment |
| V-Log | Log | See Panasonic V-Log specification |
| Canon Log 2/3 | Log | See Canon CLog specification |
| RED Log3G10 | Log | See RED Log3G10 specification |
| ACEScc | Log | `out = (log2(in) + 9.72) / 17.52` |
| ACEScct | Log | Like ACEScc but with toe |

### RGB-to-RGB Conversion
```
Convert: Source RGB → Source RGB to XYZ → Chromatic Adapt → XYZ to Dest RGB
```

Chromatic adaptation: **Bradford** (D60/D65/D50 matrix).

---

## LUT Format

### .cube Format (3D LUT)

```
TITLE "My Creative LUT"

# Domain
LUT_3D_SIZE 33
LUT_3D_INPUT_RANGE 0.0 1.0

# Data: R_out G_out B_out (one entry per grid point)
0.0 0.0 0.0
0.0 0.0 0.03125
...
```

Grid ordering: B changes fastest, then G, then R (standard).

### 3D LUT Interpolation

**Trilinear:**
```
Find cell: (r0,g0,b0) → (r1,g1,b1) where r1-r0 = 1/grid_size
fr = (r - r0) / (r1 - r0)
fg = (g - g0) / (g1 - g0)
fb = (b - b0) / (b1 - b0)
Interpolate R edge, then G plane, then B cube
```

**Tetrahedral:**
```
Subdivide cube into 6 tetrahedra. Determine which tetrahedron contains (r,g,b).
Interpolate using barycentric coordinates within tetrahedron.
Higher quality than trilinear (fewer artifacts).
```

---

## HSL Keyer (Qualifier)

Pixel selection based on Hue/Saturation/Luma:

```
h_mask = smoothstep(h_min - h_soft, h_min, hue)
       * (1.0 - smoothstep(h_max, h_max + h_soft, hue))
s_mask = smoothstep(s_min - s_soft, s_min, sat)
       * (1.0 - smoothstep(s_max, s_max + s_soft, sat))
l_mask = smoothstep(l_min - l_soft, l_min, luma)
       * (1.0 - smoothstep(l_max, l_max + l_soft, luma))

alpha = h_mask * s_mask * l_mask
alpha = smoothstep(clean_black, 1.0, alpha)  # Remove low-alpha noise
alpha = smoothstep(0.0, 1.0 - clean_white, alpha)  # Boost high-alpha
```

Where `smoothstep(edge0, edge1, x)` performs Hermite interpolation.

---

## Scope Math

### Waveform
For each pixel column (x), accumulate luminance/chroma values vertically.
X = horizontal position, Y = signal level [0–1], Brightness = density.

### Vectorscope
Each pixel's normalized color difference signals:
```
Cb = B - Y
Cr = R - Y
```
Plot (Cb, Cr) as 2D histogram. Angle = hue, Radius = saturation.

### Histogram
Count pixels per value bin (256 bins per channel).
```
bin[x] = count of pixels where channel_value ∈ [x/256, (x+1)/256)
```

### CIE Chromaticity
Convert RGB to XYZ to xy:
```
X = 0.4124564*R + 0.3575761*G + 0.1804375*B
Y = 0.2126729*R + 0.7151522*G + 0.0721750*B
Z = 0.0193339*R + 0.1191920*G + 0.9503041*B

x = X / (X + Y + Z)
y = Y / (X + Y + Z)
```

Plot (x, y) per pixel as 2D histogram. Overlay Rec709/P3/BT2020 gamut triangles.
