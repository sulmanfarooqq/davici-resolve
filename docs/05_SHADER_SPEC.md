# GLSL Shader Specifications

## Pipeline Architecture

All color processing runs in **OpenGL 3.3 Core Profile** via `QOpenGLWidget`.
Each operation renders a full-screen quad through a fragment shader.

### Standard Shader Interface

```glsl
// Vertex shader (passthrough - same for all operations)
layout(location = 0) in vec2 a_pos;
layout(location = 1) in vec2 a_tex;
out vec2 v_texcoord;
void main() {
    gl_Position = vec4(a_pos, 0.0, 1.0);
    v_texcoord = a_tex;
}

// Fragment shader (per-operation)
in vec2 v_texcoord;
uniform sampler2D u_frame;    // Input frame texture (RGBA8, [0,1])
out vec4 frag_color;           // Output color

void main() {
    vec4 color = texture(u_frame, v_texcoord);
    // ... operation-specific code ...
    frag_color = vec4(result, color.a);
}
```

### Shared FBO Pipeline

```
Input Texture → Shader A → FBO A → Shader B → FBO B → ... → Output (Viewer)
```

Each node in the graph can be rendered as one or more shader passes.
Two FBOs are used for ping-pong (no extra allocations).

---

## Shader Catalog

### 1. `common.glsl` — Shared Utilities

```glsl
// RGB ↔ HSL (single pixel)
vec3 rgb2hsl(vec3 rgb) {
    float max_c = max(max(rgb.r, rgb.g), rgb.b);
    float min_c = min(min(rgb.r, rgb.g), rgb.b);
    float l = (max_c + min_c) * 0.5;
    float s = 0.0;
    float h = 0.0;
    if (max_c != min_c) {
        float d = max_c - min_c;
        s = l > 0.5 ? d / (2.0 - max_c - min_c) : d / (max_c + min_c);
        if (max_c == rgb.r) h = (rgb.g - rgb.b) / d + (rgb.g < rgb.b ? 6.0 : 0.0);
        else if (max_c == rgb.g) h = (rgb.b - rgb.r) / d + 2.0;
        else h = (rgb.r - rgb.g) / d + 4.0;
        h /= 6.0;
    }
    return vec3(h, s, l);
}

vec3 hsl2rgb(vec3 hsl) {
    // Standard HSL→RGB conversion
    // ...
}

// 3×3 matrix transform
vec3 apply_matrix(vec3 color, mat3 m, vec3 offset) {
    return m * color + offset;
}

// Gamma correction
vec3 linear_to_gamma(vec3 linear, float g) {
    return pow(max(linear, vec3(0.0)), vec3(1.0 / g));
}

vec3 gamma_to_linear(vec3 gamma, float g) {
    return pow(max(gamma, vec3(0.0)), vec3(g));
}

// Soft clamp for highlight rolloff
vec3 soft_clamp(vec3 color, float shoulder) {
    // Smooth rolloff near 1.0
    return min(color, 1.0 - exp(-color / shoulder) * shoulder);
}

// Smoothstep with Hermite interpolation
float smoothstep(float edge0, float edge1, float x) {
    float t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
    return t * t * (3.0 - 2.0 * t);
}
```

### 2. `color_wheel.glsl` — Primary Correction

```glsl
uniform vec3  u_lift;
uniform vec3  u_gamma;
uniform vec3  u_gain;
uniform vec3  u_offset;
uniform float u_pivot;
uniform float u_contrast;
uniform float u_saturation;
uniform float u_hue;
uniform vec3  u_temp_tint;  // x=temperature, y=tint

void main() {
    vec4 color = texture(u_frame, v_texcoord);
    vec3 c = color.rgb;

    // Temperature/Tint (multiply matrix)
    c = apply_temp_tint(c, u_temp_tint.x, u_temp_tint.y);

    // Contrast with pivot
    c = (c - u_pivot) * (1.0 + u_contrast) + u_pivot;

    // Lift (offset before)
    c += u_lift;

    // Gain (multiply)
    c *= u_gain;

    // Gamma (power)
    c = pow(max(c, vec3(0.001)), 1.0 / max(u_gamma, vec3(0.001)));

    // Offset (offset after)
    c += u_offset;

    // Hue rotation
    vec3 hsl = rgb2hsl(c);
    hsl.x = mod(hsl.x + u_hue, 1.0);
    c = hsl2rgb(hsl);

    // Saturation
    float luma = dot(c, vec3(0.2126, 0.7152, 0.0722));
    c = mix(vec3(luma), c, 1.0 + u_saturation);

    gl_FragColor = vec4(clamp(c, 0.0, 1.0), color.a);
}
```

### 3. `curves.glsl` — Curve Evaluation

```glsl
uniform sampler1D u_curve_lut;  // 256×1 texture (built from control points)
uniform int       u_curve_mode; // 0=luma, 1=R, 2=G, 3=B, 4=HH, 5=HS, 6=HL, 7=LS, 8=SS, 9=SL
uniform float     u_curve_soft_clip; // 0=off, >0=soft clip amount

void main() {
    vec4 color = texture(u_frame, v_texcoord);
    vec3 c = color.rgb;
    vec3 hsl = rgb2hsl(c);

    if (u_curve_mode == 0) {  // Luma curve
        float luma = dot(c, vec3(0.2126, 0.7152, 0.0722));
        float mapped = texture(u_curve_lut, luma).r;
        c *= mapped / max(luma, 0.001);
    }
    else if (u_curve_mode >= 1 && u_curve_mode <= 3) {  // R/G/B channel
        int ch = u_curve_mode - 1;
        c[ch] = texture(u_curve_lut, c[ch]).r;
    }
    else if (u_curve_mode == 4) {  // Hue vs Hue
        float shift = texture(u_curve_lut, hsl.x).r;
        hsl.x = mod(hsl.x + shift, 1.0);
        c = hsl2rgb(hsl);
    }
    else if (u_curve_mode == 5) {  // Hue vs Sat
        float mult = texture(u_curve_lut, hsl.x).r;
        hsl.y *= mult;
        c = hsl2rgb(hsl);
    }
    // ... additional modes ...

    // Soft clip
    if (u_curve_soft_clip > 0.0) {
        c = soft_clamp(c, u_curve_soft_clip);
    }

    gl_FragColor = vec4(c, color.a);
}
```

### 4. `lut_3d.glsl` — 3D LUT Application

```glsl
uniform sampler3D u_lut;       // 3D LUT texture
uniform float     u_lut_size;  // Grid size (17, 33, 65)
uniform float     u_mix;       // Blend with original [0,1]

void main() {
    vec4 color = texture(u_frame, v_texcoord);
    vec3 c = clamp(color.rgb, 0.0, 1.0);

    // Map to LUT coordinates (accounting for half-cell offset)
    float scale = (u_lut_size - 1.0) / u_lut_size;
    float offset = 1.0 / (2.0 * u_lut_size);
    vec3 lut_coord = c * scale + offset;

    // Trilinear interpolation via hardware texture3D
    vec3 graded = texture(u_lut, lut_coord).rgb;

    // Mix with original
    vec3 result = mix(c, graded, u_mix);

    gl_FragColor = vec4(result, color.a);
}
```

### 5. `cst.glsl` — Color Space Transform

```glsl
uniform mat3  u_matrix;
uniform vec3  u_offset;
uniform float u_apply_fwd;   // 0=pass-through, 1=apply forward transform
uniform float u_apply_inv;   // 0=pass-through, 1=apply inverse
uniform vec3  u_gamma;       // gamma params
uniform vec3  u_log_params;  // log curve params (cut, a, b)

// Forward log curve: ARRI LogC, S-Log3, etc.
vec3 apply_log_fwd(vec3 c, vec3 params) {
    // params.x = cut, params.y = a, params.z = b
    return c;
}

// Inverse log curve
vec3 apply_log_inv(vec3 c, vec3 params) {
    return c;
}

void main() {
    vec4 color = texture(u_frame, v_texcoord);
    vec3 c = color.rgb;

    // Inverse log (linearize)
    if (u_apply_inv > 0.5) c = apply_log_inv(c, u_log_params);

    // Matrix transform
    c = u_matrix * c + u_offset;

    // Forward log
    if (u_apply_fwd > 0.5) c = apply_log_fwd(c, u_log_params);

    gl_FragColor = vec4(c, color.a);
}
```

### 6. `qualifier.glsl` — HSL Key

```glsl
uniform vec3 u_hue_range;  // (min, max, softness)
uniform vec3 u_sat_range;
uniform vec3 u_lum_range;
uniform float u_clean_black;
uniform float u_clean_white;

float range_mask(float value, float min_val, float max_val, float softness) {
    float low = smoothstep(min_val - softness, min_val, value);
    float high = 1.0 - smoothstep(max_val, max_val + softness, value);
    return low * high;
}

void main() {
    vec4 color = texture(u_frame, v_texcoord);
    vec3 hsl = rgb2hsl(color.rgb);

    float h_mask = range_mask(hsl.x, u_hue_range.x, u_hue_range.y, u_hue_range.z);
    float s_mask = range_mask(hsl.y, u_sat_range.x, u_sat_range.y, u_sat_range.z);
    float l_mask = range_mask(hsl.z, u_lum_range.x, u_lum_range.y, u_lum_range.z);

    float alpha = h_mask * s_mask * l_mask;

    // Clean black/white
    alpha = smoothstep(u_clean_black, 1.0, alpha);
    if (u_clean_white > 0.0)
        alpha = 1.0 - smoothstep(0.0, 1.0, alpha);

    gl_FragColor = vec4(color.rgb, alpha);
}
```

### 7. `power_window.glsl` — Shape Mask

```glsl
uniform int     u_shape;       // 0=circle, 1=rect, 2=polygon, 3=curve, 4=gradient
uniform vec2    u_center;      // normalized [0,1]
uniform vec2    u_size;        // width, height [0,1]
uniform float   u_rotation;
uniform float   u_feather;
uniform int     u_invert;
uniform vec2    u_uv_offset;   // for screen-space coords

// Shape test functions...
float circle_mask(vec2 uv, vec2 center, float radius, float feather) { ... }
float rect_mask(vec2 uv, vec2 center, vec2 size, float feather) { ... }
float polygon_mask(vec2 uv, vec2[] points, float feather) { ... }

void main() {
    vec4 color = texture(u_frame, v_texcoord);
    vec2 uv = v_texcoord + u_uv_offset;

    float mask = 0.0;
    if (u_shape == 0) mask = circle_mask(uv, u_center, u_size.x, u_feather);
    else if (u_shape == 1) mask = rect_mask(uv, u_center, u_size, u_feather);

    if (u_invert != 0) mask = 1.0 - mask;

    gl_FragColor = vec4(color.rgb, mask);
}
```

### 8. `blur.glsl` — Separable Gaussian Blur

```glsl
uniform vec2 u_radius;     // (radius_x, radius_y) in pixels
uniform vec2 u_direction;  // (1,0)=horizontal, (0,1)=vertical

const int KERNEL_SIZE = 13;
const float weights[13] = float[](
    0.0022, 0.0088, 0.0270, 0.0637, 0.1159, 0.1629, 0.1769,
    0.1629, 0.1159, 0.0637, 0.0270, 0.0088, 0.0022
);

void main() {
    vec4 color = vec4(0.0);
    vec2 texel = 1.0 / vec2(textureSize(u_frame, 0));
    vec2 step = u_direction * u_radius * texel;

    for (int i = 0; i < KERNEL_SIZE; i++) {
        float offset = float(i - KERNEL_SIZE / 2);
        color += texture(u_frame, v_texcoord + step * offset) * weights[i];
    }

    gl_FragColor = color;
}
```

### 9. `scope_waveform.glsl` — Waveform Render

```glsl
// Two-pass: (1) accumulate per-column min/max, (2) render as intensity graph

// Pass 1: Compute — reduce frame to waveform data (width × 256)
layout(rgba8) uniform image2D u_waveform_image;

void main() {
    vec4 color = texture(u_frame, v_texcoord);
    float luma = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));
    int x = int(v_texcoord.x * imageSize(u_waveform_image).x);
    int y = int(luma * 255.0);
    imageStore(u_waveform_image, ivec2(x, y), vec4(1.0));
}

// Pass 2: Render — display accumulated data
void main() {
    vec4 data = texture(u_waveform_tex, v_texcoord);
    float intensity = data.r;
    // Apply density coloring (green→yellow→red)
    vec3 color = mix(vec3(0.0, 0.05, 0.0), vec3(0.0, 1.0, 0.0), intensity);
    color = mix(color, vec3(1.0, 1.0, 0.0), max(0.0, intensity - 0.5) * 2.0);
    gl_FragColor = vec4(color, 1.0);
}
```

### 10. `scope_vectorscope.glsl` — Vectorscope Render

```glsl
// Similar two-pass structure: accumulate (Cb,Cr) histogram → display polar

void main() {
    vec4 color = texture(u_frame, v_texcoord);
    // Cb = B - Y,  Cr = R - Y
    float Y = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));
    float Cb = (color.b - Y) * 0.5 + 0.5;  // normalize to [0,1]
    float Cr = (color.r - Y) * 0.5 + 0.5;

    int x = int(Cb * 255.0);
    int y = int(Cr * 255.0);
    // Accumulate in 256×256 texture
}

// Render: convert polar, draw skin tone indicator line at ~123°
void main() {
    vec2 polar = v_texcoord - 0.5;  // center
    float angle = atan(polar.y, polar.x);
    float radius = length(polar) * 2.0;
    // Look up accumulated data at (angle, radius)
    // ... render dot density + reference markers ...
}
```

### 11. `scope_histogram.glsl` — Histogram Render

```glsl
// Accumulate 256 bins per channel (R, G, B, Y)
layout(r32f) uniform image2D u_hist_bins[4];
uniform int u_mode;  // 0=RGB, 1=Y, 2=Luma

void main() {
    vec4 color = texture(u_frame, v_texcoord);
    float luma = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));

    int bin_r = int(color.r * 255.0);
    int bin_g = int(color.g * 255.0);
    int bin_b = int(color.b * 255.0);
    int bin_y = int(luma * 255.0);

    imageAtomicAdd(u_hist_bins[0], ivec2(bin_r, 0), 1.0);
    imageAtomicAdd(u_hist_bins[1], ivec2(bin_g, 0), 1.0);
    imageAtomicAdd(u_hist_bins[2], ivec2(bin_b, 0), 1.0);
    imageAtomicAdd(u_hist_bins[3], ivec2(bin_y, 0), 1.0);
}
```

### 12. `scope_cie.glsl` — CIE Chromaticity Render

```glsl
// Convert RGB → XYZ → xy for each pixel
// Accumulate in CIE xy space (512×512 texture)
// Overlay gamut triangles for Rec709/P3/BT2020

const mat3 RGB_TO_XYZ = mat3(
    0.4124564, 0.2126729, 0.0193339,
    0.3575761, 0.7151522, 0.1191920,
    0.1804375, 0.0721750, 0.9503041
);

void main() {
    vec4 color = texture(u_frame, v_texcoord);
    vec3 xyz = RGB_TO_XYZ * color.rgb;
    float sum = xyz.x + xyz.y + xyz.z;
    float x = xyz.x / sum;
    float y = xyz.y / sum;
    // Accumulate at (x, y) position
}

void render() {
    // Draw CIE horseshoe
    // Draw gamut triangles
    // Draw accumulated pixel data
}
```
