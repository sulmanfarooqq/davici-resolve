# UI/UX Design Specification — DaVinci Resolve Color Page Clone

> Full pixel-level design reference for recreating the DaVinci Resolve Color Page
> interface. Based on analysis of Resolve 18/19/20/21 across multiple display
> configurations at 1920×1080 and 2560×1440.

---

## 1. COLOR PALETTE

### Global Theme

```
Background (deepest level):    #1a1a1e  (RGB: 26,26,30)
Panel backgrounds:             #222226  (RGB: 34,34,38)
Panel header bars:             #2a2a2e  (RGB: 42,42,46)
Dock/widget surfaces:          #2c2c30  (RGB: 44,44,48)
Hover state:                   #3a3a3e  (RGB: 58,58,62)
Active/selected:               #444448  (RGB: 68,68,72)
Pressed:                       #505054  (RGB: 80,80,84)
```

### Accent Colors

```
Primary accent (blue):         #3498db  (RGB: 52,152,219)
Secondary accent (orange):     #e67e22  (RGB: 230,126,34)
Selection highlight:           #5dade2  (RGB: 93,173,226)
Warning/error:                 #e74c3c  (RGB: 231,76,60)
Success:                       #2ecc71  (RGB: 46,204,113)
```

### Text Colors

```
Primary text:                  #cccccc  (RGB: 204,204,204)
Secondary text:                #888888  (RGB: 136,136,136)
Disabled text:                 #555555  (RGB: 85,85,85)
Bright text (on accent):       #ffffff  (RGB: 255,255,255)
Numeric values:                #d4d4d4  (RGB: 212,212,212)
```

### Node Label Colors

```
Blue:     #3498db  (default)
Green:    #2ecc71
Red:      #e74c3c
Orange:   #e67e22
Purple:   #9b59b6
Yellow:   #f1c40f
Cyan:     #1abc9c
Pink:     #e91e63
None:     transparent (uses outline)
```

### Scope Colors

```
Waveform/Parade background:    #0d0d0d
Vectorscope background:        #0a0a0a
Histogram background:          #0d0d0d
CIE background:                #1a1a2e

Waveform trace (luma):         #7fff00  (chartreuse)
Waveform grid:                 #2a2a2a
Vectorscope trace:             #7fff00
Vectorscope skin tone line:    #ff6b6b  (red)
Histogram R:                   #ff4444
Histogram G:                   #44ff44
Histogram B:                   #4444ff
Histogram luma:                #ffffff
CIE gamut triangle:            #ffffff20  (20% white)
CIE gamut outline:             #ffffff60
```

---

## 2. TYPOGRAPHY

| Element | Font | Size | Weight | Color |
|---|---|---|---|---|
| Panel headers | System UI | 11px | Bold | #888 |
| Palette labels | System UI | 11px | Normal | #ccc |
| Numeric values | System UI | 12px | Normal | #d4d4d4 |
| Slider values | System UI | 11px | Normal | #ccc |
| Button labels | System UI | 11px | Normal | #ccc |
| Node labels | System UI | 12px | Bold | #fff |
| Timeline timecode | Monospace | 11px | Normal | #ccc |
| Scope labels | System UI | 10px | Normal | #888 |
| Dropdown text | System UI | 11px | Normal | #ccc |
| Tooltips | System UI | 11px | Normal | #fff |
| Menu items | System UI | 12px | Normal | #ccc |

Font family: `"Segoe UI", "SF Pro Display", -apple-system, sans-serif`
Monospace: `"Cascadia Code", "Consolas", "SF Mono", monospace`

---

## 3. OVERALL LAYOUT — ZONE MAP

```
╔══════════════════════════════════════════════════════════════════╗
║ TOOLBAR (32px)  [File Edit Color View Render]  [Project]        ║
╠══════╦═══════════════════════════════╦═══════════════════════════╣
║      ║                               ║  NODE EDITOR             ║
║      ║                               ║  ┌─────────────────────┐ ║
║      ║                               ║  │  [N1]──▶[N2]──▶[N3] │ ║
║      ║                               ║  └─────────────────────┘ ║
║      ║      VIEWER                   ║  ┌─────────────────────┐ ║
║ LEFT ║    (QOpenGLWidget)            ║  │ [Open FX Browser]   │ ║
║ BAR  ║                               ║  └─────────────────────┘ ║
║280px ║                               ║                          ║
║      ║   [toolbar: 36px]             ║  RIGHT PANEL (320px)     ║
║      ║   [image area: fill]          ║                          ║
║      ║   [transport: 40px]           ║                          ║
║      ║                               ║                          ║
╠══════╩═══════════════════════════════╩═══════════════════════════╣
║ THUMBNAIL TIMELINE (52px)  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ║
║ MINI TIMELINE (40px)       ═══════════════════════════════════  ║
╠══════════════════════════════════════════════════════════════════╣
║ PALETTE BUTTON BAR (36px)  [Raw][Match][Primaries][HDR]...     ║
╠══════════════════════════════╦═══════════════════════════════════╣
║ ACTIVE PALETTE (variable)    ║  SCOPES / KEYFRAMES / INFO       ║
║                              ║  ┌────────────────────────────┐  ║
║  e.g. Color Wheels panel     ║  │ Waveform / Vectorscope /   │  ║
║  ┌────────────────────────┐  ║  │ Histogram / CIE            │  ║
║  │ ○ Lift                 │  ║  └────────────────────────────┘  ║
║  │ ○ Gamma               │  ║  ┌────────────────────────────┐  ║
║  │ ○ Gain                │  ║  │ Keyframes / Info           │  ║
║  │ ○ Offset              │  ║  └────────────────────────────┘  ║
║  └────────────────────────┘  ║                                   ║
║                              ║  SCOPES PANEL (360px)            ║
╠══════════════════════════════╩═══════════════════════════════════╣
║ STATUS BAR (24px)  [Frame: 00123] [Clip: 00:05:12:15] [FPS: 24] ║
╚══════════════════════════════════════════════════════════════════╝
```

### Zone Dimensions (at 1920×1080)

| Zone | Width | Height | Min Width | Notes |
|---|---|---|---|---|
| Left bar (Gallery/LUTs/Media) | 280px | Full remaining | 200px | Can be hidden |
| Viewer | Fill (rest) | Fill (rest) | 400px | Resizable with dividers |
| Right panel (Node Editor) | 320px | Full remaining | 250px | Can toggle to Open FX |
| Thumbnail timeline | Full | 52px | 52px | Can be hidden |
| Mini timeline | Full | 40px | 40px | Can be hidden |
| Palette button bar | Full | 36px | 36px | Always visible |
| Active palette content | Full | Variable | 120px | Height shares with scopes |
| Scopes panel | 360px | Variable | 200px | Shares height with palette |
| Toolbar | Full | 32px | 32px | Always visible |
| Viewer toolbar | Full of viewer | 36px | 36px | Can be hidden |
| Viewer transport | Full of viewer | 40px | 40px | Can be hidden |

At 1080p with all panels visible:
- Upper half: ~580px (Viewer + panels)
- Lower half: ~500px (timelines + palettes + scopes)

---

## 4. DETAILED PANEL DESIGNS

### 4.1 Viewer

```
┌──────────────────────────────────────────────────────┐
│ [Wipe▼] [Split▼] [Highlight] [Bypass] [Eyedropper]  │ ← 36px toolbar
│ [1:1] [Fit] [Zoom: 50%] [R] [G] [B] [Alpha]        │
├──────────────────────────────────────────────────────┤
│                                                      │
│                                                      │
│                 IMAGE DISPLAY AREA                    │
│              (QOpenGLWidget)                         │
│                                                      │
│          ○ Power window handles                      │
│          ■ Resize corners                            │
│          ─── Feather indicator                       │
│                                                      │
│                                                      │
├──────────────────────────────────────────────────────┤
│ [◀◀] [◀] [▶ Play] [▶▶] [■ Stop]  [Frame: 00123]     │ ← 40px transport
│ [In: 00100] [Out: 00200]  [00:05:12:15 / 00:30:00]  │
└──────────────────────────────────────────────────────┘
```

**Toolbar buttons (left to right):**
- Image Wipe toggle (split comparison)
- Split Screen toggle (multi-clip)
- Highlight toggle (show matte overlay)
- Bypass Grade toggle (show original)
- Eyedropper (color picker)
- Zoom level dropdown
- 1:1 / Fit toggle
- R/G/B/Alpha channel solo buttons

**Interactions:**
| Action | Behavior |
|---|---|
| Scroll wheel | Zoom in/out centered on cursor |
| Click-drag (when zoomed) | Pan image |
| Right-click (when zoomed) | Reset zoom to fit |
| Click (eyedropper mode) | Sample pixel color |
| Click-drag (eyedropper mode) | Sample average color in area |
| Click on power window edge | Select window (show handles) |
| Drag power window handle | Resize/move/rotate window |
| Double-click power window edge | Add control point |
| Ctrl+click on image | Set white balance from sample |

### 4.2 Color Wheels Panel (Primaries)

```
┌──────────────────────────────────────────────────────────────┐
│ [Wheels] [Bars] [Log] [Adjustment Controls ▼]  [Reset All]  │ ← Tab bar
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐                                  │
│  │  ○ LIFT  │  │  ○ GAMMA │    ← Color wheels (64×64 px)    │
│  │          │  │          │                                  │
│  │  ● puck  │  │  ● puck  │                                  │
│  │          │  │          │                                  │
│  │ ──── 0.00│  │ ──── 0.00│    ← Master slider below wheel  │
│  └──────────┘  └──────────┘                                  │
│  ┌──────────┐  ┌──────────┐                                  │
│  │  ○ GAIN  │  │ ○ OFFSET │                                  │
│  │          │  │          │                                  │
│  │  ● puck  │  │  ● puck  │                                  │
│  │          │  │          │                                  │
│  │ ──── 0.00│  │ ──── 1.00│                                  │
│  └──────────┘  └──────────┘                                  │
│                                                              │
│  ┌─ Contrast ──────────── ○ ────────────────┐  0.00         │
│  ┌─ Pivot ─────────────── ○ ────────────────┐  0.435        │
│  ┌─ Saturation ────────── ○ ────────────────┐  0.00         │
│  ┌─ Hue ───────────────── ○ ────────────────┐  0.00         │
│  ┌─ Temperature ───────── ○ ────────────────┐  0.00         │
│  ┌─ Tint ──────────────── ○ ────────────────┐  0.00         │
│  ┌─ Midtone Detail ────── ○ ────────────────┐  0.00         │
│  ┌─ Color Boost ───────── ○ ────────────────┐  0.00         │
│  ┌─ Shadows ───────────── ○ ────────────────┐  0.00         │
│  ┌─ Highlights ────────── ○ ────────────────┐  0.00         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Color Wheel Widget** (core interaction):
- Diameter: 64px (can scale with DPI)
- Inner circle gradient: radial gradient showing color space
- Puck: 8px diameter white circle with black border (1px)
- Puck X position: Red-Blue axis
- Puck Y position: Green-Magenta axis
- Range per axis: -1.0 to 1.0
- Master slider: horizontal bar, 4px thick, range -1.0 to 1.0
- Reset button: small "↺" icon top-right of each wheel (12×12px)

**Slider widget design:**
- Track: 4px height, rounded, dark gray (#3a3a3e)
- Fill: gradient from dark to accent (for value indication)
- Handle: 12×16px rounded rect, #888 normal, #ccc hover
- Value label: right-aligned, 60px wide, click-to-edit
- Drag behavior: horizontal drag changes value, Shift=slow, Ctrl=fast
- Double-click on label: edit numeric value directly

### 4.3 Curves Panel

```
┌──────────────────────────────────────────────────────────────┐
│ [Custom ▼]  [R] [G] [B] [Reset]  [Eyedropper]  [Soft Clip]  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                                                      │   │
│  │          CURVE CANVAS (QWidget)                      │   │
│  │                                                      │   │
│  │      ╱╲          ● Control points (6px circle)      │   │
│  │     ╱  ╲                                             │   │
│  │    ╱    ╲●         ● Selected point (8px, border)   │   │
│  │   ╱      ╲                                           │   │
│  │  ●────────╲─────── Grid lines (dashed, 1px, #333)   │   │
│  │             ╲                                        │   │
│  │              ●═══    Histogram overlay (dim)         │   │
│  │                                                      │   │
│  │  [0,0]                                   [1,1]      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  HSL Curves: [H/H] [H/S] [H/L] [L/S] [S/S] [S/L]          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Canvas specs:**
- Drawing area: fills available space (min 200×200px)
- Grid: 4×4 divisions, dashed lines (#2a2a2a), 1px
- Diagonal line (identity): #555, 1px
- Curve line: #fff or accent, 2px, anti-aliased
- Control points: 6px filled circle, white
- Selected control point: 8px circle, white fill + #3498db border 2px
- Histogram background: dim trace (#ffffff10)
- Spline interpolation: Catmull-Rom (smooth through all points)
- Soft clip: optional, shows as rounded-off top-right corner of curve

**Interactions:**
| Action | Behavior |
|---|---|
| Click on curve | Add control point |
| Drag control point | Move point (snaps to grid with Shift) |
| Double-click control point | Delete point (min 2 points) |
| Click empty area | Deselect |
| Click-drag in empty area | Marquee select multiple points |
| Delete key | Remove selected points |
| Ctrl+Z/Y | Undo/redo curve edit |

### 4.4 Qualifier Panel

```
┌──────────────────────────────────────────────────────────────┐
│ [Eyedropper] [3D Preview] [Highlight] [Invert] [Reset]      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Hue:    ┌─██████▓▓▓▓▓▓▓▓████░░░░░────┐                     │
│          ▒▒    0.00          0.40       ▒▒  Soft: 0.10       │
│  Sat:    ┌─████████████████████░░░░░────┐                     │
│          ▒▒    0.00          0.80       ▒▒  Soft: 0.05       │
│  Luma:   ┌─████████████████████████─────┐                     │
│          ▒▒    0.05          0.95       ▒▒  Soft: 0.05       │
│                                                              │
│  ┌─ Clean Black ────────── ○ ────────────┐  0.00            │
│  ┌─ Clean White ────────── ○ ────────────┐  0.00            │
│                                                              │
│  ┌── Matte Finesse ──────── [▸ Expand] ─┐                   │
│  │  Blur Radius:  [───○───]  0.00       │                   │
│  │  Erode:        [───○───]  0.00       │                   │
│  │  Dilate:       [───○───]  0.00       │                   │
│  └───────────────────────────────────────┘                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Gradient bar widget:**
- Background: gradient representing the full H/S/L range
- Selection range: highlighted region between min/max handles
- Softness: lighter highlighted area outside min/max (fade)
- Handles: triangular markers at min/max (8px tall)
- Drag handle: move min/max bound
- Drag middle: move entire range (preserving width)
- Drag softness edges: adjust falloff

### 4.5 Power Window Panel

```
┌──────────────────────────────────────────────────────────────┐
│ [● Circle] [▬ Rect] [⬠ Polygon] [⤴ Curve] [▨ Gradient]     │ ← Shape selector
│ [Inside ▼] [Invert ■]  [Reset Shape]                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ Center X ──────────── ○ ────────────┐  0.50             │
│  ┌─ Center Y ──────────── ○ ────────────┐  0.50             │
│  ┌─ Width ─────────────── ○ ────────────┐  0.50             │
│  ┌─ Height ────────────── ○ ────────────┐  0.50             │
│  ┌─ Rotation ──────────── ○ ────────────┐  0.00°            │
│  ┌─ Feather ───────────── ○ ────────────┐  0.10             │
│                                                              │
│  ┌── Tracking ──────────── [▸ Expand] ─┐                    │
│  │ [Track Fwd] [Track Rev] [Reset]     │                    │
│  │ Mode: [Pan] [Tilt] [Zoom] [Rot]     │                    │
│  └──────────────────────────────────────┘                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4.6 Scopes Panel

```
┌──────────────────────────────────────────────────────────────┐
│ [Waveform ▼] [Parade] [Vectorscope] [Histogram] [CIE]       │ ← Scope tabs
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                                                      │    │
│  │   WAVEFORM / PARADE / VECTORSCOPE / HISTOGRAM       │    │
│  │                                                      │    │
│  │   (Rendered via QOpenGLWidget on quarter-res frame)  │    │
│  │                                                      │    │
│  │   Waveform: x=position, y=luma, color=density       │    │
│  │   Parade: side-by-side R/G/B waveforms              │    │
│  │   Vectorscope: polar plot, skin tone line at 123°   │    │
│  │   Histogram: RGB/Y distribution, 256 bins            │    │
│  │   CIE: xy chromaticity with gamut triangles          │    │
│  │                                                      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Settings: [Opacity: 80%] [Grid] [Skin Tone Line] [Gamut]   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Scope widgets — unified design specs:**
- Background: #0d0d0d
- Grid lines: #1a1a1a (minor), #2a2a2a (major)
- Trace color: chartreuse (#7fff00) for luma/chroma
- Overlay outlines: white at 40% opacity
- Border: 1px #333
- Default size for single scope: fill area (typically 360×240px)
- All scopes update every 100ms during playback (10fps refresh)
- Computed at quarter resolution for performance

### 4.7 Node Editor

```
┌──────────────────────────────────────────────────────────────┐
│ [＋ Add Node ▼] [Bypass All] [Solo] [Clean Up] [Fit] [◉]    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                                                      │    │
│  │    Input ──── [N1] ──── [N2] ──── [N3] ──── Output  │    │
│  │                │ BLUE       │          │              │    │
│  │                │┌──────────┐│          │              │    │
│  │                ││ Color    ││          │              │    │
│  │                ││ Wheel    ││          │              │    │
│  │                │└──────────┘│          │              │    │
│  │                │            ├──────────┤              │    │
│  │                │            │ Parallel │              │    │
│  │                │ [N4]───────┤  Mix     │              │    │
│  │                │ GREEN     │└──────────┘              │    │
│  │                │┌──────────┐                          │    │
│  │                ││ Curves   │                          │    │
│  │                │└──────────┘                          │    │
│  │                                                      │    │
│  │    QGraphicsView / QGraphicsScene                    │    │
│  │    - Bezel-curve edges between sockets               │    │
│  │    - Nodes are QGraphicsItems                        │    │
│  │    - Drag to pan, scroll to zoom                     │    │
│  │                                                      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Node widget design:**
```
┌──────────────────────────────┐
│ ● Input Socket (8px circle)  │
│                              │
│   ┌──────────────────────┐   │
│   │  Color Wheel Node    │ ← Header bar (node color) 28px
│   │  [Primary Grade]     │ ← Label area
│   └──────────────────────┘   │
│                              │
│  ○ Output Socket (8px circle)│
└──────────────────────────────┘
```

| Element | Size | Style |
|---|---|---|
| Node width | 160px | — |
| Node min height | 60px | Grows with content |
| Header bar height | 28px | Colored by node color (default #3498db) |
| Border | 1px | #555 (idle), #fff (selected) |
| Border radius | 4px | All corners |
| Input/output sockets | 8px circle | Empty = #555, Filled = #888 |
| Connected socket | 8px circle | Filled with accent color |
| Socket margin | 6px from edge | — |
| Label font | 12px Bold | White |

**Edge (connection) design:**
- Cubic bezier from source socket to destination socket
- Line width: 2px
- Color: #555 (idle), accent (selected)
- Hover: highlight to 3px, lighten color

**Interactions:**
| Action | Behavior |
|---|---|
| Click-drag from socket | Draw connection line (rubber band) |
| Release on socket | Create edge (if valid) |
| Release on empty | No edge created |
| Click edge | Select (highlight) |
| Delete selected edge | Remove connection |
| Double-click empty | Add node menu |
| Click-drag node body | Move node |
| Right-click node | Context menu (Label, Color, Bypass, Solo, Delete) |
| Ctrl+C / Ctrl+V | Copy/paste selected node(s) |
| Middle-click drag | Pan canvas |
| Scroll | Zoom canvas (0.25× to 4×) |

### 4.8 Timeline

```
┌──────────────────────────────────────────────────────────────┐
│ [▼ Timeline Options]  [＋ Add]  [Link]  [Zoom: ▬○▬]        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │ ← Thumbnails (52px)
│  │  │  Clip_A  │  Clip_B  │  Clip_C  │  Clip_D  │     │    │
│  │  │          │          │          │          │     │    │
│  │  └──────────┴──────────┴──────────┴──────────┘     │    │
│  └──────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ ──────────────────────■────────────────────────────  │ ← Mini timeline (40px)
│  │ Track 1: Video ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   │    │
│  │ Track 2: Video ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Thumbnail timeline:**
- Height: 52px (includes 2px padding)
- Each clip shown as thumbnail image
- Clip name label below thumbnail (11px, #ccc)
- Highlight border on current clip (2px #3498db)
- Playhead: vertical line, 2px, #ffffff, extends through both timelines
- Click on thumbnail: jump to clip
- Scroll: pan through clips

**Mini timeline:**
- Height: 40px
- Shows track structure like edit page mini-timeline
- Waveforms shown for audio tracks
- Playhead syncs with thumbnail timeline
- Click to seek, drag playhead to scrub

### 4.9 Palette Button Bar

```
┌──────────────────────────────────────────────────────────────┐
│ Left: [Camera Raw] [ColorMatch] [Primaries] [HDR] [RGBMix]│
│       [MotionFX]                                            │
│ Center:[Curves] [ColorSlice] [ColorWarp] [Qualifier]       │
│        [Window] [Tracker] [MagicMask] [Blur] [Key]          │
│        [Sizing] [3D]                                        │
│ Right: [Keyframes ▼] [Scopes ▼] [Info]                     │
└──────────────────────────────────────────────────────────────┘
```

**Button design:**
- Height: 36px
- Width: auto (text + padding), min 60px
- Inactive: #2a2a2e bg, #888 text
- Hover: #3a3a3e bg, #ccc text
- Active (selected palette): #3498db bg, #fff text, 1px brighter border
- Active palette indicator: underline or 2px bottom accent bar
- Group separators: 1px #444 vertical line between left/center/right groups

### 4.10 Gallery Panel

```
┌──────────────────────────────────────────────┐
│ [Grab Still] [＋ Album] [Import] [Export]    │ ← 32px toolbar
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────┐  ┌──────┐  ┌──────┐              │
│  │      │  │      │  │      │  ← Stills     │
│  │ img  │  │ img  │  │ img  │    120×68px   │
│  │      │  │      │  │      │              │
│  └──────┘  └──────┘  └──────┘              │
│  ┌──────┐  ┌──────┐  ┌──────┐              │
│  │      │  │      │  │      │              │
│  │ img  │  │ img  │  │ img  │              │
│  │      │  │      │  │      │              │
│  └──────┘  └──────┘  └──────┘              │
│                                              │
│  Albums: [Master] [Scene 1] [Scene 2]       │
│                                              │
└──────────────────────────────────────────────┘
```

**Still thumbnail:**
- Size: 120×68px (maintains 16:9 ratio)
- Border: 1px #444 (idle), 2px #3498db (selected)
- Thumbnail count badge: top-right corner, 16px, #3498db
- Context menu: Apply Grade, Delete, Export, Compare

### 4.11 LUT Browser

```
┌──────────────────────────────────────────────┐
│ [Import LUTs] [Refresh] [Search...          ]│
├──────────────────────────────────────────────┤
│                                              │
│  ┌─ Folder Tree ──────────────────────────┐  │
│  │  ▼ LUTs                               │  │
│  │    ├─ Creative                        │  │
│  │    │  ├─ FilmLooks                    │  │
│  │    │  │  ├─ Kodak2383.cube          │  │
│  │    │  │  ├─ Fuji3510.cube           │  │
│  │    │  └─ ...                         │  │
│  │    ├─ Technical                      │  │
│  │    │  ├─ LogC_to_Rec709.cube         │  │
│  │    │  └─ SLog3_to_Rec709.cube        │  │
│  │    └─ User                           │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  Preview: Hover to preview on viewer         │
│  Apply: Drag to node or right-click node     │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 5. WIDGET DESIGN SPECS

### 5.1 Color Wheel Widget

```
Layout:
┌──────────────────┐
│  ↺ Reset  ○      │  ← 12px reset button, 64px wheel
│          ●       │
│       ───○───    │  ← Master slider, 54px wide
│        0.00      │  ← Value label
└──────────────────┘
```

### 5.2 Color Slider

```
┌────────────────────────────────────┐
│ Contrast      ●━━━━━━━━━○────────  │ 0.00
│               label     handle    value
```

**Dimensions:**
- Total height: 24px per slider row
- Label width: 100px left-aligned
- Track: fill remaining width, 4px height, rounded (#3a3a3e)
- Fill: colored portion from 0 to handle position (#3498db)
- Handle: 12×16px rounded rectangle (#888)
- Value: 50px right-aligned, #d4d4d4

### 5.3 Numeric Drag Widget

```
  ┌────────────────────────┐
  │  Contrast     [+0.00]  │
  └────────────────────────┘
```

- Click-drag on value: adjust up/down
- Shift+drag: 10× finer adjustment
- Ctrl+drag: 10× coarser adjustment
- Double-click: enter exact value via keyboard
- Hover: show tooltip with full range info

### 5.4 Gradient Bar (Qualifier range)

```
  ┌────────────────────────────────────┐
  │ ▒▒ ████████▓▓▓▓▓▓▓▓▓████████▒▒    │
  │    ^      ^         ^      ^       │
  │  soft_min min       max   soft_max │
  └────────────────────────────────────┘
```

- Height: 20px
- Background: full range gradient
- Soft zone (outside min/max): dimmer/lighter
- Selected zone (between min/max): brighter
- Handle: triangular grip at min/max

### 5.5 Dropdown / Combo Box

- Height: 24px
- Background: #2c2c30
- Hover: #3a3a3e
- Text: #ccc, 11px
- Arrow: 12×12 down arrow icon (#888)
- Menu: 1px #444 border, items 24px each, hover highlight

### 5.6 Button Styles

| Type | Height | Min Width | Bg Normal | Bg Hover | Bg Active | Text |
|---|---|---|---|---|---|---|
| Toolbar icon | 28px | 28px | transparent | #3a3a3e | #444448 | — |
| Palette button | 36px | 60px | #2a2a2e | #3a3a3e | #3498db | #ccc |
| Text button | 24px | auto | transparent | #3a3a3e | #444448 | #ccc |
| Icon button | 24px | 24px | transparent | #3a3a3e | #444448 | — |
| Reset | 16px | 16px | transparent | #e74c3c40 | #e74c3c60 | — |

### 5.7 Tab Bar

- Height: 28px
- Inactive tab: #2a2a2e bg, #888 text
- Active tab: #3498db bg (or thicker bottom border), #fff text
- Tab padding: 8px horizontal
- Tab spacing: 0px (adjacent)
- Bottom border: 1px #444

---

## 6. DIVIDERS AND RESIZE HANDLES

| Divider | Thickness | Color | Hover Color | Cursor |
|---|---|---|---|---|
| Vertical (viewer/panels) | 4px | #1a1a1e | #3498db | SizeHorCursor |
| Horizontal (palettes/scopes) | 4px | #1a1a1e | #3498db | SizeVerCursor |
| Small grip dots | 2px | #444 | #888 | — |

Double-click on divider: auto-adjust to split 50/50.

---

## 7. TOOLBAR AND MENU BAR

### Menu Bar
- Height: 32px
- Background: #1a1a1e
- Items: File | Edit | Color | View | Render | Workspace | Help
- Item padding: 12px horizontal
- Item hover: #2a2a2e

### Toolbar Icons
- Size: 20×20px SVG
- Color: #888 (inactive), #ccc (active/hover)
- All icons from a single icon set for consistency
- Categories: transport (play/pause/prev/next), tool (eyedropper/zoom/pan), view (fit/1:1/overlay)

---

## 8. TOOLTIPS

- Delay: 500ms before showing
- Background: #2a2a2e (with slight transparency)
- Border: 1px #444
- Text: #fff, 11px
- Padding: 4px 8px
- Max width: 300px
- Position: follows cursor (offset +12px, +20px)
- Show parameter name, current value, and min/max range

---

## 9. CONTEXT MENUS

- Background: #2a2a2e
- Border: 1px #555
- Item height: 28px
- Item padding: 8px 16px
- Item hover: #3a3a3e
- Separator: 1px #444
- Submenu indicator: ► at right edge
- Shadow: 4px drop shadow at 30% opacity

---

## 10. RESPONSIVE BEHAVIOR

### Layout Adaptations

| Screen Width | Behavior |
|---|---|
| >1920px | Full layout: all panels visible, 3-column palette view |
| 1600–1920px | Full layout, slightly narrower panels |
| 1366–1600px | Left bar collapses to icons only (expand on hover/click) |
| 1024–1366px | Left bar hidden by default. Right panel tabs: nodes/effects collapsed |
| <1024px | Palette switches to 2-column layout. Scopes tabified with palette |

### Palette Layout Columns

| Width | Palette Columns |
|---|---|
| >1600px | 3 columns (default) |
| 1024–1600px | 2 columns |
| <1024px | 1 column (scrollable) |

### Viewer Zoom States

| State | Key | Behavior |
|---|---|---|
| Normal | — | Viewer in layout |
| Enhanced | Alt+F | Viewer expands to fill most of screen, panels collapse |
| Full Screen | Shift+F | Viewer fills entire screen with UI chrome |
| Cinema | Ctrl+F | Viewer fills entire screen, no chrome |

---

## 11. ANIMATION AND TRANSITIONS

| Element | Property | Duration | Easing |
|---|---|---|---|
| Panel expand/collapse | Width/Height | 200ms | ease-in-out |
| Tab switch | Opacity | 100ms | linear |
| Hover highlight | Background color | 80ms | linear |
| Puck drag | None (instant) | — | — |
| Node selection | Border color | 100ms | linear |
| Connection drag | Continuous | — | — |
| Scope update | Texture swap | Next frame | — |
| Tooltip show | Opacity | 150ms | ease-out |
| Context menu | Opacity + Position | 100ms | ease-out |
| Splitter drag | None (continuous) | — | — |

---

## 12. ICON SPECIFICATIONS

- Format: SVG (scalable)
- Base size: 20×20px (toolbar), 16×16px (panel internals)
- Stroke width: 1.5px
- Stroke color: currentColor (inherits from CSS)
- Fill: none (except for special icons like filled shapes)
- Corner radius: 2px for square icon elements

### Required Icons

| Icon | Usage |
|---|---|
| Play | Transport |
| Pause | Transport |
| Prev Frame | Transport |
| Next Frame | Transport |
| Go to Start | Transport |
| Go to End | Transport |
| Eyedropper | Viewer toolbar, Qualifier |
| Fit | Viewer zoom |
| 1:1 | Viewer zoom |
| Zoom In | Viewer zoom |
| Wipe | Compare mode |
| Split Screen | Compare mode |
| Highlight | Matte preview |
| Bypass | Toggle grade |
| Reset | All panels |
| Expand | Panel expand |
| Collapse | Panel collapse |
| Add Node | Node editor |
| Trash | Delete |
| Plus | Add/grab |
| Gear | Settings |
| Grid | Scope grid |
| Skin Tone | Vectorscope indicator |
| Lock | Tracker lock |
| Track Forward | Tracker |
| Track Reverse | Tracker |
| Grab Still | Gallery |
| Album | Gallery |
| Folder | LUT browser |
| Search | LUT browser |
| Chevron Down | Dropdown |
| Chevron Right | Collapsible section |

---

## 13. DARK THEME QSS (PySide6 Reference)

```css
/* Main Window */
QMainWindow {
    background-color: #1a1a1e;
}

/* Dock Widgets */
QDockWidget {
    background-color: #222226;
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}

QDockWidget::title {
    background-color: #2a2a2e;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: bold;
    color: #888888;
}

/* QOpenGLWidget (Viewer) */
QOpenGLWidget {
    background-color: #000000;
}

/* Scrollbars */
QScrollBar:vertical {
    width: 8px;
    background: #1a1a1e;
}
QScrollBar::handle:vertical {
    background: #3a3a3e;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #505054;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 4px;
    background: #3a3a3e;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 12px;
    height: 16px;
    background: #888888;
    border-radius: 2px;
    margin: -6px 0;
}
QSlider::handle:horizontal:hover {
    background: #cccccc;
}

/* Buttons */
QPushButton {
    background-color: #2c2c30;
    color: #cccccc;
    border: 1px solid #444444;
    border-radius: 3px;
    padding: 4px 10px;
    font-size: 11px;
}
QPushButton:hover {
    background-color: #3a3a3e;
}
QPushButton:pressed {
    background-color: #505054;
}
QPushButton:checked {
    background-color: #3498db;
    color: #ffffff;
    border-color: #2980b9;
}

/* Line Edit */
QLineEdit {
    background-color: #2c2c30;
    color: #cccccc;
    border: 1px solid #444444;
    border-radius: 2px;
    padding: 2px 6px;
    font-size: 11px;
}
QLineEdit:focus {
    border-color: #3498db;
}

/* Combo Box */
QComboBox {
    background-color: #2c2c30;
    color: #cccccc;
    border: 1px solid #444444;
    border-radius: 3px;
    padding: 2px 8px;
    font-size: 11px;
}
QComboBox:hover {
    border-color: #888888;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #2a2a2e;
    border: 1px solid #444444;
    selection-background-color: #3a3a3e;
    color: #cccccc;
}

/* Tab Widget */
QTabWidget::pane {
    background-color: #222226;
    border: none;
}
QTabBar::tab {
    background-color: #2a2a2e;
    color: #888888;
    border: none;
    padding: 4px 12px;
    font-size: 11px;
}
QTabBar::tab:selected {
    background-color: #3498db;
    color: #ffffff;
}
QTabBar::tab:hover:!selected {
    background-color: #3a3a3e;
}

/* Tooltip */
QToolTip {
    background-color: #2a2a2e;
    color: #ffffff;
    border: 1px solid #444444;
    padding: 4px 8px;
    font-size: 11px;
}

/* Menu */
QMenu {
    background-color: #2a2a2e;
    border: 1px solid #555555;
    padding: 4px 0;
}
QMenu::item {
    padding: 4px 16px;
    font-size: 12px;
    color: #cccccc;
}
QMenu::item:selected {
    background-color: #3a3a3e;
}
QMenu::separator {
    height: 1px;
    background: #444444;
    margin: 4px 8px;
}
```

---

## 14. ACCESSIBILITY

- Minimum click target: 24×24px
- Tab order: top-left to bottom-right
- All controls keyboard-navigable
- Focus indicator: 1px dashed #3498db around focused element
- All values modifiable via keyboard entry
- Color blind friendly: scopes use patterns + colors, not just color
- High contrast mode: invert icons, increase border contrast

---

## Appendix: Widget Reference Index

| Widget | File in Project | Parent Class |
|---|---|---|
| Color Wheel | `ui/widgets/color_wheel_widget.py` | QWidget |
| Color Slider | `ui/widgets/color_slider.py` | QWidget |
| Numeric Drag | `ui/widgets/numeric_drag.py` | QWidget |
| Curve Canvas | `ui/widgets/curve_canvas.py` | QWidget |
| Scope GL | `ui/widgets/scope_gl.py` | QOpenGLWidget |
| Gradient Bar | `ui/widgets/gradient_slider.py` | QWidget |
| Timeline Strip | `ui/widgets/timeline_widget.py` | QWidget |
| Palette Button Bar | `ui/widgets/palette_button_bar.py` | QWidget |
| Viewer GL | `ui/viewer/viewer_gl.py` | QOpenGLWidget |
| Node Editor | `ui/panels/node_editor_panel.py` | QGraphicsView |
| All Panels | `ui/panels/*.py` | QWidget / QDockWidget |
