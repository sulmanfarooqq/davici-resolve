"""Main window — DaVinci Resolve Color Page style layout with all integrations."""

import os
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QPushButton, QLabel, QSlider, QFileDialog,
    QMenuBar, QToolBar, QStatusBar, QDockWidget, QScrollArea,
    QFrame, QGraphicsView, QGraphicsScene, QMessageBox, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QImage, QPixmap, QPainter, QColor, QPen, QShortcut, QKeySequence

from ui.app_state import AppState
from core.video_io import VideoReader
from core.frame_cache import FrameCache
from core.playback_controller import PlaybackController, PlaybackState
from core.color_math import (
    colorbalance_lgg, colorbalance_cdl, apply_brightness_contrast,
    apply_saturation, apply_exposure, apply_gamma, apply_invert,
    rgb_to_hsv,
)
from core.lut_parser import parse_cube, cube_to_lut3d, apply_lut_3d
from core.project import Project, GradeParams, add_recent_file, get_recent_files
from core.undo_manager import UndoManager, GradeSnapshot
from core.node_graph import NodeGraph

from ui.widgets.transport_bar import TransportBar
from ui.widgets.timeline_widget import TimelineWidget
from ui.widgets.node_editor import NodeEditor
from ui.widgets.scope_gl import ScopeGL
from ui.panels.color_slice import ColorSlicePanel
from ui.panels.color_warper import ColorWarperPanel
from ui.panels.power_windows import PowerWindowsPanel
from ui.panels.tracker import TrackerPanel
from ui.panels.gallery import GalleryPanel
from ui.panels.lut_browser import LUTBrowserPanel
from ui.panels.info_panel import InfoPanel
from nodes import NODE_CLASSES


class ViewerGL(QWidget):
    cursor_moved = Signal(int, int, float, float, float)
    color_picked = Signal(float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #000000;")
        self._pixmap = None
        self._frame_array = None
        self._zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._dragging = False
        self._drag_start = None
        self._tracker_bbox = None
        self._pipette_mode = False
        self.setMouseTracking(True)

    def set_image(self, rgb_array: np.ndarray):
        if rgb_array is None:
            self._pixmap = None
            self._frame_array = None
            self.update()
            return
        self._frame_array = rgb_array
        h, w = rgb_array.shape[:2]
        rgb8 = np.clip(rgb_array * 255.0, 0, 255).astype(np.uint8) if rgb_array.dtype != np.uint8 else rgb_array
        qimg = QImage(rgb8.data, w, h, w * 3, QImage.Format_RGB888)
        self._pixmap = QPixmap.fromImage(qimg)
        self._fit_to_widget()
        self.update()

    def _fit_to_widget(self):
        if self._pixmap is None:
            return
        pw = self._pixmap.width()
        ph = self._pixmap.height()
        sw = self.width()
        sh = self.height()
        scale = min(sw / pw, sh / ph, 1.0) * 0.95
        self._zoom = scale
        self._pan_x = (sw - pw * scale) / 2
        self._pan_y = (sh - ph * scale) / 2

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        if self._pixmap:
            painter.save()
            painter.translate(self._pan_x, self._pan_y)
            painter.scale(self._zoom, self._zoom)
            painter.drawPixmap(0, 0, self._pixmap)
            if self._tracker_bbox is not None:
                x, y, w, h = self._tracker_bbox
                pen = QPen(QColor(0, 255, 0), 2)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(int(x), int(y), int(w), int(h))
            painter.restore()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        factor = 1.1 if delta > 0 else 0.9
        self._zoom *= factor
        self._zoom = max(0.05, min(self._zoom, 50.0))
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._pipette_mode and self._frame_array is not None and self._pixmap is not None:
                pw = self._pixmap.width()
                ph = self._pixmap.height()
                img_x = int((event.pos().x() - self._pan_x) / self._zoom)
                img_y = int((event.pos().y() - self._pan_y) / self._zoom)
                h, w = self._frame_array.shape[:2]
                fx = int(img_x * w / pw) if pw > 0 else 0
                fy = int(img_y * h / ph) if ph > 0 else 0
                fx = max(0, min(fx, w - 1))
                fy = max(0, min(fy, h - 1))
                r, g, b = self._frame_array[fy, fx, :3]
                self.color_picked.emit(float(r), float(g), float(b))
                self._pipette_mode = False
                self.setCursor(Qt.ArrowCursor)
                return
            self._dragging = True
            self._drag_start = (event.pos().x(), event.pos().y())
        elif event.button() == Qt.RightButton:
            self._fit_to_widget()
            self.update()

    def mouseMoveEvent(self, event):
        if self._dragging and self._drag_start:
            dx = event.pos().x() - self._drag_start[0]
            dy = event.pos().y() - self._drag_start[1]
            self._pan_x += dx
            self._pan_y += dy
            self._drag_start = (event.pos().x(), event.pos().y())
            self.update()
        if self._frame_array is not None and self._pixmap is not None:
            pw = self._pixmap.width()
            ph = self._pixmap.height()
            img_x = int((event.pos().x() - self._pan_x) / self._zoom)
            img_y = int((event.pos().y() - self._pan_y) / self._zoom)
            if 0 <= img_x < pw and 0 <= img_y < ph:
                h, w = self._frame_array.shape[:2]
                fx = int(img_x * w / pw)
                fy = int(img_y * h / ph)
                fx = max(0, min(fx, w - 1))
                fy = max(0, min(fy, h - 1))
                r, g, b = self._frame_array[fy, fx, :3]
                self.cursor_moved.emit(fx, fy, float(r), float(g), float(b))

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def set_tracker_bbox(self, bbox):
        self._tracker_bbox = bbox
        self.update()

    def set_pipette_mode(self, enabled=True):
        self._pipette_mode = enabled
        if enabled:
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)


class ColorWheelWidget(QWidget):
    valueChanged = Signal(tuple)

    def __init__(self, label="", size=70, parent=None):
        super().__init__(parent)
        self.label = label
        self._size = size
        self._radius = size // 2 - 4
        self._cx = size // 2 + 10
        self._cy = size // 2 + 5
        self._value = (0.0, 0.0)
        self._dragging = False
        self.setFixedSize(size + 20, size + 30)

    def set_value(self, x, y):
        self._value = (x, y)
        self.update()

    def reset(self):
        self._value = (0.0, 0.0)
        self.update()
        self.valueChanged.emit(self._value)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self._radius
        cx, cy = self._cx, self._cy
        for i in range(64):
            a1 = (i / 64) * 6.2832
            a2 = ((i + 1) / 64) * 6.2832
            h = i / 64
            h6 = h * 6.0
            hi = int(h6)
            f = h6 - hi
            rgb = [(1.0, f, 0.0), (1.0 - f, 1.0, 0.0), (0.0, 1.0, f),
                   (0.0, 1.0 - f, 1.0), (f, 0.0, 1.0), (1.0, 0.0, 1.0 - f)][hi]
            color = QColor(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawPie(cx - r, cy - r, r*2, r*2, int(a1 * 5760 / 3.14159), int((a2 - a1) * 5760 / 3.14159))
        for i in range(8):
            t = i / 8
            ir = r * t
            painter.setBrush(QColor(0, 0, 0, int(100 * (1 - t))))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx - ir, cy - ir, ir*2, ir*2)
        painter.setPen(QPen(QColor("#555"), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(cx - r, cy - r, r*2, r*2)
        px = cx + self._value[0] * r * 0.7
        py = cy + self._value[1] * r * 0.7
        painter.setPen(QPen(QColor("#333"), 1))
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(px - 5, py - 5, 10, 10)
        painter.setPen(QColor("#888"))
        painter.drawText(0, self._size + 15, self._size + 20, 15, Qt.AlignCenter, self.label)

    def mousePressEvent(self, event):
        self._dragging = True
        self._update_puck(event.pos())

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._update_puck(event.pos())

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def _update_puck(self, pos):
        dx = pos.x() - self._cx
        dy = pos.y() - self._cy
        max_d = self._radius * 0.7
        dist = (dx*dx + dy*dy) ** 0.5
        if dist > max_d:
            dx = dx / dist * max_d
            dy = dy / dist * max_d
        self._value = (dx / max_d, dy / max_d)
        self.update()
        self.valueChanged.emit(self._value)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("davici-resolve — Color Grading Panel")
        self.setMinimumSize(1400, 850)

        self.app_state = AppState()
        self.video_reader = VideoReader()
        self.frame_cache = FrameCache()
        self.playback = PlaybackController(self.video_reader, self.frame_cache)
        self.undo_manager = UndoManager()
        self.current_frame = None
        self.original_frame = None
        self.current_project_path = None
        self.current_lut_path = None
        self._channel_visible = {'R': True, 'G': True, 'B': True, 'Alpha': True}
        self._pipette_active = False
        self.grade_params = {
            'lift': [0.0, 0.0, 0.0], 'gamma': [1.0, 1.0, 1.0],
            'gain': [1.0, 1.0, 1.0], 'offset': [0.0, 0.0, 0.0],
            'contrast': 0.0, 'saturation': 0.0, 'exposure': 0.0,
            'temp': 0.0, 'tint': 0.0,
        }
        self.lut = None
        self.node_graph = NodeGraph()
        self._build_ui()
        self._setup_shortcuts()

    def _build_ui(self):
        self._build_menubar()
        self._build_toolbar()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        top_split = QSplitter(Qt.Horizontal)
        main_layout.addWidget(top_split, 1)

        viewer_container = QWidget()
        v_layout = QVBoxLayout(viewer_container)
        v_layout.setContentsMargins(2, 2, 2, 2)
        v_layout.setSpacing(2)
        self.viewer = ViewerGL()
        self.viewer.cursor_moved.connect(self._on_cursor_moved)
        self.viewer.color_picked.connect(self._on_color_picked)
        v_layout.addWidget(self.viewer, 1)
        vt = QHBoxLayout()
        for text, slot in [("Fit", self._fit_viewer), ("1:1", self._zoom_100),
                           ("R", self._toggle_red), ("G", self._toggle_green), ("B", self._toggle_blue),
                           ("Alpha", self._toggle_alpha)]:
            btn = QPushButton(text)
            btn.setFixedHeight(24)
            btn.setCheckable(True)
            setattr(self, f'_ch_{text.lower()}', btn)
            btn.clicked.connect(slot)
            vt.addWidget(btn)
        self._pipette_btn = QPushButton("Pick")
        self._pipette_btn.setFixedHeight(24)
        self._pipette_btn.setCheckable(True)
        self._pipette_btn.clicked.connect(self._toggle_pipette)
        vt.addWidget(self._pipette_btn)
        v_layout.addLayout(vt)
        top_split.addWidget(viewer_container)

        right_tabs = QTabWidget()
        right_tabs.setMinimumWidth(280)
        self.node_editor = NodeEditor(self.node_graph, NODE_CLASSES)
        self.node_editor.graph_changed.connect(self._on_node_graph_changed)
        right_tabs.addTab(self.node_editor, "Node Editor")
        right_tabs.addTab(self._build_fx_tab(), "Open FX")
        self.gallery_panel = GalleryPanel()
        self.gallery_panel.still_loaded.connect(self._on_gallery_still_loaded)
        right_tabs.addTab(self.gallery_panel, "Gallery")
        self.lut_browser_panel = LUTBrowserPanel()
        self.lut_browser_panel.lut_applied.connect(self._on_lut_browser_applied)
        right_tabs.addTab(self.lut_browser_panel, "LUT Browser")
        top_split.addWidget(right_tabs)
        top_split.setSizes([800, 300])

        bottom_widget = QWidget()
        b_layout = QVBoxLayout(bottom_widget)
        b_layout.setContentsMargins(0, 0, 0, 0)
        b_layout.setSpacing(0)

        self._build_palette_bar(b_layout)

        pal_scope_split = QSplitter(Qt.Horizontal)
        b_layout.addWidget(pal_scope_split, 1)

        self.palette_stack = QTabWidget()
        self.palette_stack.setMinimumHeight(150)
        self._build_primaries_tab()
        self._build_curves_tab()
        self._build_keying_tab()
        self._build_color_slice_tab()   # index 3
        self._build_color_warper_tab()  # index 4
        self._build_power_windows_tab() # index 5
        self.palette_stack.setCurrentIndex(0)
        pal_scope_split.addWidget(self.palette_stack)

        scopes_and_info = QTabWidget()
        scopes_and_info.setMinimumWidth(300)
        self.scope_waveform = ScopeGL()
        self.scope_waveform.set_mode('waveform')
        scopes_and_info.addTab(self.scope_waveform, "Waveform")
        self.scope_histogram = ScopeGL()
        self.scope_histogram.set_mode('histogram')
        scopes_and_info.addTab(self.scope_histogram, "Histogram")
        self.scope_vectorscope = ScopeGL()
        self.scope_vectorscope.set_mode('vectorscope')
        scopes_and_info.addTab(self.scope_vectorscope, "Vectorscope")
        self.info_panel = InfoPanel()
        scopes_and_info.addTab(self.info_panel, "Info")
        pal_scope_split.addWidget(scopes_and_info)
        pal_scope_split.setSizes([500, 350])

        main_layout.addWidget(bottom_widget, 0)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("No media loaded")
        self.status_bar.addWidget(self.status_label)

        self._scope_timer = QTimer()
        self._scope_timer.timeout.connect(self._update_scopes)
        self._scope_timer.start(200)

    def _build_menubar(self):
        mb = self.menuBar()
        file_menu = mb.addMenu("File")
        file_menu.addAction("New Project", self._new_project)
        file_menu.addAction("Open Project...", self._open_project)
        file_menu.addAction("Save Project", self._save_project)
        file_menu.addAction("Save Project As...", self._save_project_as)
        file_menu.addSeparator()
        file_menu.addAction("Open Image...", self._open_image)
        file_menu.addAction("Open Video...", self._open_video)
        file_menu.addAction("Open LUT...", self._open_lut)
        file_menu.addSeparator()
        self._recent_menu = file_menu.addMenu("Recent Files")
        self._refresh_recent()
        file_menu.addSeparator()
        file_menu.addAction("Export Frame...", self._export_frame)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        edit_menu = mb.addMenu("Edit")
        edit_menu.addAction("Undo", self._undo).setShortcut(QKeySequence.Undo)
        edit_menu.addAction("Redo", self._redo).setShortcut(QKeySequence("Ctrl+Shift+Z"))
        edit_menu.addSeparator()
        edit_menu.addAction("Reset Grade", self._reset_grade)
        edit_menu.addAction("Reset All", self._reset_all)

        view_menu = mb.addMenu("View")
        self._show_scopes_action = view_menu.addAction("Scopes")
        self._show_scopes_action.setCheckable(True)
        self._show_scopes_action.setChecked(True)

    def _build_toolbar(self):
        self.transport = TransportBar()
        self.transport.play_pause_clicked.connect(self._on_play_pause)
        self.transport.stop_clicked.connect(lambda: self.playback.stop())
        self.transport.step_forward_clicked.connect(lambda: self.playback.step_forward())
        self.transport.step_backward_clicked.connect(lambda: self.playback.step_backward())
        self.transport.speed_changed.connect(lambda s: self.playback.set_speed(s))
        self.addToolBar(self.transport)
        self.playback.state_changed.connect(self._on_playback_state)
        self.playback.frame_changed.connect(self._on_frame_changed)
        self.playback.frame_ready.connect(self._on_frame_ready)

    def _build_palette_bar(self, layout):
        bar = QWidget()
        bar.setFixedHeight(32)
        bar.setStyleSheet("background-color: #222226;")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(4, 2, 4, 2)
        bl.setSpacing(2)
        palette_info = [
            ("Primaries", 0), ("Curves", 1), ("Keying", 2),
            ("ColorSlice", 3), ("Color Warper", 4), ("Windows", 5),
        ]
        self._palette_btns = []
        for name, idx in palette_info:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setFixedHeight(24)
            if idx == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, i=idx: self._switch_palette(i))
            bl.addWidget(btn)
            self._palette_btns.append(btn)
        bl.addStretch()
        layout.addWidget(bar)

    def _switch_palette(self, idx):
        for i, btn in enumerate(self._palette_btns):
            btn.setChecked(i == idx)
        if idx < self.palette_stack.count():
            self.palette_stack.setCurrentIndex(idx)

    def _build_primaries_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        wheels_frame = QWidget()
        wl = QVBoxLayout(wheels_frame)

        def make_wheel(label, key):
            w = ColorWheelWidget(label=label, size=60)
            def on_change(val):
                self.grade_params[key][0] = val[0]
                self.grade_params[key][1] = val[1]
                self._push_undo()
                self._update_grade()
            w.valueChanged.connect(on_change)
            return w

        row1 = QHBoxLayout()
        self.lift_wheel = make_wheel("LIFT", 'lift')
        self.gamma_wheel = make_wheel("GAMMA", 'gamma')
        row1.addWidget(self.lift_wheel)
        row1.addWidget(self.gamma_wheel)
        wl.addLayout(row1)

        row2 = QHBoxLayout()
        self.gain_wheel = make_wheel("GAIN", 'gain')
        self.offset_wheel = make_wheel("OFFSET", 'offset')
        row2.addWidget(self.gain_wheel)
        row2.addWidget(self.offset_wheel)
        wl.addLayout(row2)
        wl.addStretch()
        layout.addWidget(wheels_frame)

        sliders_frame = QWidget()
        sl = QVBoxLayout(sliders_frame)
        self._sliders = {}
        for name, key, lo, hi, default in [
            ("Contrast", 'contrast', -1.0, 1.0, 0.0),
            ("Saturation", 'saturation', -1.0, 1.0, 0.0),
            ("Exposure", 'exposure', -5.0, 5.0, 0.0),
            ("Temperature", 'temp', -1.0, 1.0, 0.0),
            ("Tint", 'tint', -1.0, 1.0, 0.0),
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(name))
            slider = QSlider(Qt.Horizontal)
            slider.setRange(int(lo*100), int(hi*100))
            slider.setValue(int(default*100))
            val_label = QLabel(f"{default:.2f}")
            val_label.setFixedWidth(50)
            def make_cb(k=key, vl=val_label):
                def cb(v):
                    val = int(v) / 100.0
                    self.grade_params[k] = val
                    vl.setText(f"{val:.2f}")
                    self._push_undo()
                    self._update_grade()
                return cb
            slider.valueChanged.connect(make_cb())
            row.addWidget(slider, 1)
            row.addWidget(val_label)
            sl.addLayout(row)
            self._sliders[key] = slider
        sl.addStretch()
        layout.addWidget(sliders_frame)
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self._reset_grade)
        sl.addWidget(reset_btn)
        self.palette_stack.addTab(tab, "Primaries")

    def _build_curves_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("RGB Curves"))
        from ui.widgets.curve_canvas import CurveCanvas
        self.curve_canvas = CurveCanvas()
        self.curve_canvas.setMinimumHeight(150)
        layout.addWidget(self.curve_canvas, 1)
        hsl_row = QHBoxLayout()
        for name in ["H/H", "H/S", "H/L", "L/S", "S/S"]:
            hsl_row.addWidget(QPushButton(name))
        layout.addLayout(hsl_row)
        self.palette_stack.addTab(tab, "Curves")

    def _build_keying_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Keyer (Qualifier)"))
        kb = QPushButton("Pick Key Color")
        layout.addWidget(kb)
        for name in ["Hue Range", "Sat Range", "Luma Range"]:
            row = QHBoxLayout()
            row.addWidget(QLabel(name))
            sl = QSlider(Qt.Horizontal)
            row.addWidget(sl)
            layout.addLayout(row)
        self.palette_stack.addTab(tab, "Keying")

    def _build_color_slice_tab(self):
        self.color_slice = ColorSlicePanel()
        self.color_slice.values_changed.connect(self._on_color_slice_changed)
        self.palette_stack.addTab(self.color_slice, "ColorSlice")

    def _build_color_warper_tab(self):
        self.color_warper = ColorWarperPanel()
        self.color_warper.values_changed.connect(self._on_color_warper_changed)
        self.palette_stack.addTab(self.color_warper, "Color Warper")

    def _build_power_windows_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.power_windows = PowerWindowsPanel()
        self.power_windows.mask_changed.connect(self._on_mask_changed)
        layout.addWidget(self.power_windows)
        self.tracker_panel = TrackerPanel()
        self.tracker_panel.track_data.connect(self._on_track_data)
        layout.addWidget(self.tracker_panel)
        self.palette_stack.addTab(tab, "Windows")

    def _build_fx_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Open FX Browser"))
        for name in ["Blur", "Glow", "Sharpen", "Vignette", "Film Grain",
                      "Shadows/Highlights", "Split Toning", "Color Temperature"]:
            btn = QPushButton(name)
            btn.setStyleSheet("""QPushButton { background-color: #333; color: #888; border: 1px solid #444;
                border-radius: 4px; padding: 6px 10px; font-size: 12px; }
                QPushButton:hover { background-color: #444; color: #aaa; }""")
            layout.addWidget(btn)
        layout.addStretch()
        return tab

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self._open_image)
        QShortcut(QKeySequence("Ctrl+Shift+O"), self).activated.connect(self._open_video)
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self._open_lut)
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self._reset_grade)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self._save_project)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self).activated.connect(self._save_project_as)
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self._undo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self).activated.connect(self._redo)
        QShortcut(QKeySequence("Space"), self).activated.connect(self._on_play_pause)

    # ─── Playback ───

    def _on_play_pause(self):
        if self.playback.state == PlaybackState.PLAYING:
            self.playback.pause()
        else:
            self.playback.play()

    def _on_playback_state(self, state):
        self.transport.set_playing(state == PlaybackState.PLAYING)

    def _on_frame_changed(self, index):
        self.transport.update_frame_info(index, self.video_reader.total_frames)
        self.app_state.current_frame_index = index

    def _on_frame_ready(self, index, frame):
        self.original_frame = frame.astype(np.float32) / 255.0
        self._update_grade()

    # ─── Panel backends ───

    def _on_color_slice_changed(self, vals):
        self._push_undo()
        self._update_grade()

    def _on_color_warper_changed(self, grid):
        self._push_undo()
        self._update_grade()

    def _on_mask_changed(self, masks):
        self._update_grade()

    def _on_track_data(self, data):
        self.status_label.setText(f"Tracker: {len(data)} points tracked")
        if data and len(data) > 0:
            bbox = data[-1][1]
            self.viewer.set_tracker_bbox(bbox)

    def _on_gallery_still_loaded(self, frame, grade):
        self.original_frame = frame.copy().astype(np.float32)
        self.grade_params.update(grade)
        self._update_grade()

    def _on_lut_browser_applied(self, lut):
        self.lut = lut
        self.current_lut_path = getattr(lut, 'path', None)
        self.status_label.setText("LUT applied from browser")
        self._update_grade()

    # ─── Viewer callbacks ───

    def _on_cursor_moved(self, x, y, r, g, b):
        hsv = rgb_to_hsv(np.array([[[r, g, b]]]))[0, 0]
        self.info_panel.update_cursor_info({
            'position': f"({x}, {y})",
            'rgb': f"({r:.3f}, {g:.3f}, {b:.3f})",
            'hsv': f"({hsv[0]:.3f}, {hsv[1]:.3f}, {hsv[2]:.3f})",
        })

    def _toggle_red(self):
        self._channel_visible['R'] = not self._channel_visible['R']
        self._update_grade()

    def _toggle_green(self):
        self._channel_visible['G'] = not self._channel_visible['G']
        self._update_grade()

    def _toggle_blue(self):
        self._channel_visible['B'] = not self._channel_visible['B']
        self._update_grade()

    def _toggle_alpha(self):
        self._channel_visible['Alpha'] = not self._channel_visible['Alpha']
        self._update_grade()

    def _toggle_pipette(self):
        self._pipette_active = not self._pipette_active
        self._pipette_btn.setChecked(self._pipette_active)
        self.viewer.set_pipette_mode(self._pipette_active)

    def _on_color_picked(self, r, g, b):
        self._pipette_active = False
        self._pipette_btn.setChecked(False)
        hsv = rgb_to_hsv(np.array([[[r, g, b]]]))[0, 0]
        self.info_panel.update_cursor_info({
            'position': 'Picked',
            'rgb': f"({r:.3f}, {g:.3f}, {b:.3f})",
            'hsv': f"({hsv[0]:.3f}, {hsv[1]:.3f}, {hsv[2]:.3f})",
        })
        self.status_label.setText(f"Color picked: RGB({r:.3f}, {g:.3f}, {b:.3f})")

    # ─── Project ───

    def _new_project(self):
        self._reset_all()
        self.current_project_path = None
        self.setWindowTitle("davici-resolve — Color Grading Panel")

    def _open_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "DaVici Project (*.daviciproj)")
        if not path:
            return
        try:
            project = Project.load(path)
            self.current_project_path = path
            self._apply_project(project)
            add_recent_file(path)
            self._refresh_recent()
            self.setWindowTitle(f"davici-resolve — {os.path.basename(path)}")
            self.status_label.setText(f"Project loaded: {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load project: {e}")

    def _save_project(self):
        if self.current_project_path:
            self._write_project(self.current_project_path)
        else:
            self._save_project_as()

    def _save_project_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Project As", "", "DaVici Project (*.daviciproj)")
        if path:
            if not path.endswith('.daviciproj'):
                path += '.daviciproj'
            self._write_project(path)
            self.current_project_path = path
            add_recent_file(path)
            self._refresh_recent()
            self.setWindowTitle(f"davici-resolve — {os.path.basename(path)}")

    def _write_project(self, path):
        project = Project(
            media_path=self.video_reader.path if self.video_reader.is_open else None,
            grade=GradeParams(
                lift=self.grade_params['lift'], gamma=self.grade_params['gamma'],
                gain=self.grade_params['gain'], offset=self.grade_params['offset'],
                contrast=self.grade_params['contrast'],
                saturation=self.grade_params['saturation'],
                exposure=self.grade_params['exposure'],
                lut_path=self.current_lut_path,
            ),
            node_graph=self.node_graph.to_dict() if self.node_graph.nodes else None,
        )
        project.save(path)

    def _apply_project(self, project: Project):
        self._reset_grade()
        if project.media_path and os.path.exists(project.media_path):
            if self.video_reader.open(project.media_path):
                self.status_label.setText(f"Media: {os.path.basename(project.media_path)}")
                self.info_panel.update_image_info({
                    'dimensions': f"{self.video_reader.width}x{self.video_reader.height}",
                    'fps': f"{self.video_reader.fps:.2f}",
                })
        g = project.grade
        self.grade_params.update({
            'lift': g.lift, 'gamma': g.gamma, 'gain': g.gain,
            'offset': g.offset, 'contrast': g.contrast,
            'saturation': g.saturation, 'exposure': g.exposure,
        })
        if g.lut_path and os.path.exists(g.lut_path):
            lut = cube_to_lut3d(g.lut_path)
            if lut is not None:
                self.lut = lut
                self.current_lut_path = g.lut_path
        if project.node_graph:
            self.node_graph = NodeGraph.from_dict(project.node_graph, NODE_CLASSES)
            self.node_editor.rebuild()
        self._update_grade()

    def _refresh_recent(self):
        self._recent_menu.clear()
        for path in get_recent_files():
            self._recent_menu.addAction(path, lambda p=path: self._open_recent(p))

    def _open_recent(self, path):
        if path.endswith('.daviciproj'):
            project = Project.load(path)
            self.current_project_path = path
            self._apply_project(project)

    # ─── Undo / Redo ───

    def _push_undo(self):
        self.undo_manager.push_state(GradeSnapshot(
            grade_params=self.grade_params.copy(),
            lut_path=self._get_lut_path(),
        ))

    def _get_lut_path(self):
        return self.current_lut_path

    def _undo(self):
        snap = self.undo_manager.undo()
        if snap:
            self._restore_snapshot(snap)

    def _redo(self):
        snap = self.undo_manager.redo()
        if snap:
            self._restore_snapshot(snap)

    def _restore_snapshot(self, snap: GradeSnapshot):
        self.grade_params.update(snap.grade_params)
        if snap.lut_path != self.current_lut_path:
            if snap.lut_path and os.path.exists(snap.lut_path):
                lut = cube_to_lut3d(snap.lut_path)
                if lut is not None:
                    self.lut = lut
                    self.current_lut_path = snap.lut_path
            elif snap.lut_path is None:
                self.lut = None
                self.current_lut_path = None
        self._update_grade()

    # ─── Media loading ───

    def _open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "Images (*.png *.jpg *.jpeg *.tif *.tiff *.bmp *.exr *.dpx);;All (*)")
        if not path:
            return
        from PIL import Image
        try:
            img = Image.open(path).convert('RGB')
            arr = np.array(img, dtype=np.float32) / 255.0
            self.original_frame = arr.copy()
            self.current_frame = arr.copy()
            self.status_label.setText(f"Loaded: {os.path.basename(path)}")
            self.info_panel.update_image_info({
                'dimensions': f"{arr.shape[1]}x{arr.shape[0]}",
                'bit_depth': '8-bit (PIL)',
                'color_space': 'sRGB',
                'fps': '-',
            })
            self._update_grade()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _open_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Video", "",
            "Video (*.mp4 *.mov *.avi *.mkv *.webm *.mxf *.mts);;All (*)")
        if not path:
            return
        if self.video_reader.open(path):
            self.status_label.setText(f"Loaded: {os.path.basename(path)} — {self.video_reader.total_frames} frames")
            self.info_panel.update_image_info({
                'dimensions': f"{self.video_reader.width}x{self.video_reader.height}",
                'fps': f"{self.video_reader.fps:.2f}",
                'bit_depth': '8-bit',
                'color_space': 'Rec.709',
            })
            self.tracker_panel.set_reader(self.video_reader)
            frame = self.video_reader.read_frame(0)
            if frame is not None:
                self.original_frame = frame.astype(np.float32) / 255.0
                self._update_grade()
            add_recent_file(path)
            self._refresh_recent()
        else:
            QMessageBox.warning(self, "Error", "Could not open video file")

    def _open_lut(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open LUT", "", "Cube LUT (*.cube)")
        if not path:
            return
        lut = cube_to_lut3d(path)
        if lut is not None:
            self.lut = lut
            self.current_lut_path = path
            self.status_label.setText(f"LUT loaded: {os.path.basename(path)}")
            self._update_grade()
        else:
            QMessageBox.warning(self, "Error", "Invalid 3D LUT")

    # ─── Grading ───

    def _update_grade(self):
        if self.original_frame is None:
            return
        img = self.original_frame.copy().astype(np.float32)
        p = self.grade_params
        for c in range(3):
            l = p['lift'][c]
            g = 1.0 / max(p['gamma'][c], 0.001)
            gn = p['gain'][c]
            img[:,:,c] = colorbalance_lgg(img[:,:,c], l, g, gn)
        img[:,:,:3] += np.array(p['offset'])
        if p['contrast'] != 0.0:
            img = apply_brightness_contrast(img, 0.0, p['contrast'])
        if p['saturation'] != 0.0:
            img = apply_saturation(img, p['saturation'])
        if p['exposure'] != 0.0:
            img = apply_exposure(img, p['exposure'])
        if self.lut is not None:
            img = apply_lut_3d(img, self.lut)
        if hasattr(self, 'color_slice') and self.color_slice is not None:
            img = self.color_slice.apply_to_image(img)
        if hasattr(self, 'power_windows') and self.power_windows is not None:
            mask = self.power_windows.render_mask(img.shape[1], img.shape[0])
            if mask is not None and mask.max() > 0:
                img = img * (1.0 - mask[:,:,None]) + self.original_frame * mask[:,:,None]
        self.current_frame = np.clip(img, 0.0, 1.0)
        display = self.current_frame.copy()
        if not self._channel_visible['R']:
            display[..., 0] = 0
        if not self._channel_visible['G']:
            display[..., 1] = 0
        if not self._channel_visible['B']:
            display[..., 2] = 0
        if not self._channel_visible['Alpha'] and display.shape[-1] >= 4:
            display[..., 3] = 1.0
        self.viewer.set_image(display)

    def _update_scopes(self):
        if self.current_frame is None:
            return
        self.scope_waveform.set_image(self.current_frame)
        self.scope_histogram.set_image(self.current_frame)
        self.scope_vectorscope.set_image(self.current_frame)

    def _fit_viewer(self):
        self.viewer._fit_to_widget()
        self.viewer.update()

    def _zoom_100(self):
        self.viewer._zoom = 1.0
        self.viewer._pan_x = 0
        self.viewer._pan_y = 0
        self.viewer.update()

    def _export_frame(self):
        if self.current_frame is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Frame", "", "PNG (*.png);;JPEG (*.jpg);;TIFF (*.tif)")
        if path:
            from PIL import Image
            arr = np.clip(self.current_frame * 255.0, 0, 255).astype(np.uint8)
            Image.fromarray(arr).save(path)

    def _reset_grade(self):
        self.grade_params = {
            'lift': [0.0, 0.0, 0.0], 'gamma': [1.0, 1.0, 1.0],
            'gain': [1.0, 1.0, 1.0], 'offset': [0.0, 0.0, 0.0],
            'contrast': 0.0, 'saturation': 0.0, 'exposure': 0.0,
            'temp': 0.0, 'tint': 0.0,
        }
        self.lift_wheel.reset()
        self.gamma_wheel.reset()
        self.gain_wheel.reset()
        self.offset_wheel.reset()
        for slider in self._sliders.values():
            slider.setValue(0)
        self._push_undo()
        self._update_grade()

    def _reset_all(self):
        self._reset_grade()
        self.lut = None
        self.current_lut_path = None
        if self.original_frame is not None:
            self.current_frame = self.original_frame.copy()
            self.viewer.set_image(self.current_frame)

    def _on_node_graph_changed(self):
        self._push_undo()
