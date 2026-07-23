# davici-resolve — Final Production Implementation Plan

## Overview
This document defines the final 5-phase implementation plan to transform davici-resolve from a functional prototype into a production-grade color grading application. All 242 existing tests must continue to pass after each phase.

---

## Phase 1: Core Pipeline Wiring
**Goal:** Make every existing UI control actually process images through the grading pipeline.

### Tasks
| # | Task | File(s) | Verification |
|---|------|---------|-------------|
| 1.1 | Wire `NodeGraph.execute()` into `_update_grade()` so nodes process the image | `ui/main_window.py` | Add a Blur node via Open FX tab, verify viewer shows blurred image |
| 1.2 | Wire RGB Curves canvas `curveChanged` signal to `_update_grade()` via `node_rgb_curves()` | `ui/main_window.py`, `ui/widgets/curve_canvas.py` | Edit curve, verify viewer updates with curve applied |
| 1.3 | Wire Color Warper grid to `_update_grade()` via `apply_color_warp()` | `ui/main_window.py`, `core/color_warper.py` | Drag warper point, verify viewer updates |
| 1.4 | Wire FX tab buttons to call `_add_fx_node()` which creates and adds node to graph | `ui/main_window.py` | Click "+ Blur" in FX tab, verify node appears in Node Editor and effect applies |
| 1.5 | Wire Keying tab "Pick Key Color" button and sliders to qualifier mask logic in `_update_grade()` | `ui/main_window.py` | Pick a key color, adjust sliders, verify selective grading |
| 1.6 | Wire Gallery "Grab Still" to capture current graded frame + grade params | `ui/main_window.py`, `ui/panels/gallery.py` | Press Ctrl+D, verify still appears in gallery list |
| 1.7 | Connect `_show_scopes_action.toggled` to show/hide scopes panel | `ui/main_window.py` | Toggle View > Show Scopes, verify scopes hide/show |
| 1.8 | Node Editor bypass toggle actually skips node during execution | `core/node_graph.py` | Add 2 nodes, bypass one, verify only unbypassed node affects output |

### Verification Checklist
- [ ] Load an image, add Blur node via FX tab → image appears blurred
- [ ] Edit RGB curve → viewer updates in real-time
- [ ] Drag Color Warper point → viewer updates
- [ ] Pick key color + adjust sliders → selective area graded
- [ ] Ctrl+D grabs a still that appears in Gallery
- [ ] Toggle scopes visibility from View menu
- [ ] Bypass a node → its effect disappears from viewer
- [ ] All 242 tests still pass

---

## Phase 2: Professional Viewer Features
**Goal:** Implement before/after comparison views like DaVinci Resolve.

### Tasks
| # | Task | File(s) | Verification |
|---|------|---------|-------------|
| 2.1 | Add "Split" button to viewer toolbar that toggles before/after split view | `ui/main_window.py` | Click "Split" → viewer shows graded on one side, original on other |
| 2.2 | Split view shows original (before) on left/top, graded (after) on right/bottom | `ui/main_window.py` (`ViewerGL.paintEvent`) | Verify split shows correct before/after |
| 2.3 | Draggable split position divider (white vertical line) | `ui/main_window.py` (`ViewerGL`) | Drag divider left/right, verify split updates |
| 2.4 | Add horizontal/vertical split mode toggle | `ui/main_window.py` | Toggle between H/V split, verify orientation changes |
| 2.5 | Scope update shows graded image only (not split) | `ui/main_window.py` | In split mode, scopes still show graded image data |

### Verification Checklist
- [ ] "Split" button toggles before/after view
- [ ] Left side = original, right side = graded
- [ ] White divider line is draggable
- [ ] H/V split modes both work
- [ ] Scopes still update correctly in split mode
- [ ] All 242 tests still pass

---

## Phase 3: Production Export & Color Pipeline
**Goal:** Batch export and color space management for professional workflows.

### Tasks
| # | Task | File(s) | Verification |
|---|------|---------|-------------|
| 3.1 | Create `BatchExportDialog` with folder selection, format picker (PNG/JPG/TIFF), quality slider | `core/batch_export.py` | Open File > Batch Export, select folder, verify file count displays |
| 3.2 | Export worker thread processes all images through current grade pipeline | `core/batch_export.py` | Click Export, verify output files are graded |
| 3.3 | Add color space dropdown to primaries tab (sRGB, Rec.709, Rec.2020, ACEScg) | `ui/main_window.py`, `core/color_space.py` | Select different color spaces, verify viewer updates |
| 3.4 | Grade pipeline applies color space conversion before/after processing | `ui/main_window.py` | Change color space, verify no visual shift for same-space operations |
| 3.5 | Support high-bit image loading (16-bit TIFF, EXR) via PIL/OpenCV | `ui/main_window.py` | Load a 16-bit TIFF, verify it displays correctly |
| 3.6 | Export frame supports PNG, JPEG, TIFF with quality options | `ui/main_window.py` | Export frame in each format, verify output files |

### Verification Checklist
- [ ] File > Batch Export opens dialog with folder browser
- [ ] Batch export processes all images in folder
- [ ] Color space dropdown changes working space
- [ ] 16-bit images load correctly
- [ ] Frame export works for PNG/JPEG/TIFF
- [ ] All 242 tests still pass

---

## Phase 4: Advanced Grading Tools
**Goal:** Interactive power windows and tracker region selection.

### Tasks
| # | Task | File(s) | Verification |
|---|------|---------|-------------|
| 4.1 | Add interactive shape drawing on viewer (drag to create circle/rectangle) | `ui/main_window.py` (`ViewerGL`), `ui/panels/power_windows.py` | Select Circle in Windows tab, drag on viewer, verify mask appears |
| 4.2 | Shape parameters (center, size) update when user draws on viewer | `ui/panels/power_windows.py` | Draw shape, verify mask list updates with correct params |
| 4.3 | Gradient mask rendering (linear gradient from center to edge) | `ui/panels/power_windows.py` | Add Gradient mask, verify smooth gradient mask renders |
| 4.4 | Tracker reads bbox from viewer interaction (drag to select region) | `ui/main_window.py`, `ui/panels/tracker.py` | Right-click drag on viewer to select region, verify tracker panel receives bbox |
| 4.5 | HSL curve buttons switch CurveCanvas active channel | `ui/main_window.py`, `ui/widgets/curve_canvas.py` | Click R/G/B buttons in Curves tab, verify curve editor switches channels |
| 4.6 | Power window mask applies only the graded region (not full image composite) | `ui/main_window.py` | Draw window, apply grade, verify only inside mask is graded |

### Verification Checklist
- [ ] Draw circle on viewer → mask appears in power windows list
- [ ] Draw rectangle on viewer → correct mask generated
- [ ] Gradient mask shows smooth falloff
- [ ] Tracker region can be selected by dragging on viewer
- [ ] HSL/R/G/B curve buttons switch the curve editor channel
- [ ] Power windows correctly mask the grading effect
- [ ] All 242 tests still pass

---

## Phase 5: Version Management & Final Polish
**Goal:** Complete version system, keyboard shortcuts, and final integration.

### Tasks
| # | Task | File(s) | Verification |
|---|------|---------|-------------|
| 5.1 | Version management: Add version saves current grade+LUT+nodes | `ui/main_window.py`, `core/version_manager.py` | Click "Add Version", verify version appears in list |
| 5.2 | Double-click version to load it (restores grade, LUT, nodes) | `ui/main_window.py` | Add 2 versions, switch between them, verify grade changes |
| 5.3 | Delete and rename versions work correctly | `ui/main_window.py` | Delete a version, rename one, verify list updates |
| 5.4 | Versions persist in project save/load | `ui/main_window.py`, `core/project.py` | Save project with versions, reload, verify versions restored |
| 5.5 | Complete keyboard shortcut set (all shortcuts documented and working) | `ui/main_window.py` | Test every shortcut listed in docs |
| 5.6 | Node graph save/load roundtrip works with version system | `core/node_graph.py`, `core/project.py` | Add nodes, save project, reload, verify nodes restored |
| 5.7 | Final integration test: full workflow from load → grade → export | Manual | Load video, grade with wheels+curves+nodes+LUT, export frame |

### Verification Checklist
- [ ] Add/select/delete/rename versions all work
- [ ] Versions persist across project save/load
- [ ] All keyboard shortcuts work (Ctrl+Z, Ctrl+S, Ctrl+E, etc.)
- [ ] Node graph saves and restores correctly
- [ ] Full workflow: Load → Grade → Export produces correct output
- [ ] All 242 tests still pass
- [ ] Application launches without errors

---

## Summary

| Phase | Description | New Files | Modified Files | Est. Complexity |
|-------|-------------|-----------|---------------|-----------------|
| 1 | Core Pipeline Wiring | 0 | 3 | Medium |
| 2 | Professional Viewer | 0 | 1 | Medium |
| 3 | Export & Color Pipeline | 1 | 2 | High |
| 4 | Advanced Grading Tools | 0 | 3 | High |
| 5 | Version Management & Polish | 0 | 2 | Medium |

**Total:** ~9 files modified/created, all 242 tests passing, production-ready application.
