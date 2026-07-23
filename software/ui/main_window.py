"""Main window — DaVinci Resolve Color Page style layout with all integrations.
Complete production version with node graph execution, curves, warper,
split view, keying, power windows, gallery, versions, batch export, and more.
"""

import os
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QPushButton, QLabel, QSlider, QFileDialog,
    QToolBar, QStatusBar, QMessageBox, QSizePolicy, QComboBox,
    QInputDialog, QListWidget, QListWidgetItem, QCheckBox, QSpinBox,
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
from PySide6.QtGui import QAction, QImage, QPixmap, QPainter, QColor, QPen, QShortcut, QKeySequence

from ui.app_state import AppState
from core.video_io import VideoReader
from core.frame_cache import FrameCache
from core.playback_controller import PlaybackController, PlaybackState
from core.color_math import (
    colorbalance_lgg, colorbalance_lgg_rgb, colorbalance_cdl, apply_brightness_contrast,
    apply_saturation, apply_exposure, apply_gamma, apply_invert,
    rgb_to_hsv, GradingCache,
)
from core.curves_nodes import node_rgb_curves, node_hue_correct
from core.lut_parser import parse_cube, cube_to_lut3d, apply_lut_3d
from core.project import Project, GradeParams, add_recent_file, get_recent_files
from core.undo_manager import UndoManager, GradeSnapshot
from core.node_graph import NodeGraph
from core.color_warper import apply_color_warp
from core.version_manager import VersionManager

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

    split_toggled = Signal(bool)
    region_selected = Signal(object)
    shape_drawn = Signal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #000000;")
        self._pixmap = None
        self._pixmap_before = None
        self._frame_array = None
        self._zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._dragging = False
        self._drag_start = None
        self._tracker_bbox = None
        self._pipette_mode = False
        self._split_mode = False
        self._split_horizontal = False
        self._split_pos = 0.5
        self._split_dragging = False
        self._shape_mode = None
        self._shape_start = None
        self._shape_current = None
        self._region_mode = False
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

    def set_image_before(self, rgb_array: np.ndarray):
        if rgb_array is None:
            self._pixmap_before = None
            return
        h, w = rgb_array.shape[:2]
        rgb8 = np.clip(rgb_array * 255.0, 0, 255).astype(np.uint8) if rgb_array.dtype != np.uint8 else rgb_array
        qimg = QImage(rgb8.data, w, h, w * 3, QImage.Format_RGB888)
        self._pixmap_before = QPixmap.fromImage(qimg)

    def set_split_mode(self, enabled: bool):
        self._split_mode = enabled
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
            if self._split_mode and self._pixmap_before:
                pw = self._pixmap.width()
                ph = self._pixmap.height()
                if self._split_horizontal:
                    split_y = int(ph * self._split_pos)
                    painter.setClipRect(0, 0, pw, split_y)
                    painter.drawPixmap(0, 0, self._pixmap)
                    painter.setClipRect(0, split_y, pw, ph - split_y)
                    painter.drawPixmap(0, 0, self._pixmap_before)
                    painter.setClipping(False)
                    pen = QPen(QColor(255, 255, 255), 2)
                    painter.setPen(pen)
                    painter.drawLine(0, split_y, pw, split_y)
                else:
                    split_x = int(pw * self._split_pos)
                    painter.setClipRect(0, 0, split_x, ph)
                    painter.drawPixmap(0, 0, self._pixmap)
                    painter.setClipRect(split_x, 0, pw - split_x, ph)
                    painter.drawPixmap(0, 0, self._pixmap_before)
                    painter.setClipping(False)
                    pen = QPen(QColor(255, 255, 255), 2)
                    painter.setPen(pen)
                    painter.drawLine(split_x, 0, split_x, ph)
            else:
                painter.drawPixmap(0, 0, self._pixmap)
            if self._tracker_bbox is not None:
                x, y, w, h = self._tracker_bbox
                pen = QPen(QColor(0, 255, 0), 2)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(int(x), int(y), int(w), int(h))
            if self._shape_start and self._shape_current and self._shape_mode:
                pen = QPen(QColor(255, 255, 0), 2, Qt.DashLine)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                sx, sy = self._shape_start
                cx, cy = self._shape_current
                if self._shape_mode == 'Circle':
                    rx = abs(cx - sx)
                    ry = abs(cy - sy)
                    r = max(rx, ry)
                    painter.drawEllipse(int(sx - r), int(sy - r), int(r * 2), int(r * 2))
                else:
                    x0, y0 = min(sx, cx), min(sy, cy)
                    w, h = abs(cx - sx), abs(cy - sy)
                    painter.drawRect(int(x0), int(y0), int(w), int(h))
            if self._region_mode and self._shape_start and self._shape_current:
                pen = QPen(QColor(0, 200, 255), 2, Qt.DashDotLine)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                sx, sy = self._shape_start
                cx, cy = self._shape_current
                x0, y0 = min(sx, cx), min(sy, cy)
                w, h = abs(cx - sx), abs(cy - sy)
                painter.drawRect(int(x0), int(y0), int(w), int(h))
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
            if self._shape_mode and self._pixmap:
                img_x = (event.pos().x() - self._pan_x) / self._zoom
                img_y = (event.pos().y() - self._pan_y) / self._zoom
                self._shape_start = (img_x, img_y)
                self._shape_current = (img_x, img_y)
                return
            if self._region_mode and self._pixmap:
                img_x = (event.pos().x() - self._pan_x) / self._zoom
                img_y = (event.pos().y() - self._pan_y) / self._zoom
                self._shape_start = (img_x, img_y)
                self._shape_current = (img_x, img_y)
                return
            if self._split_mode and self._pixmap:
                img_x = (event.pos().x() - self._pan_x) / self._zoom
                img_y = (event.pos().y() - self._pan_y) / self._zoom
                pw = self._pixmap.width()
                ph = self._pixmap.height()
                if self._split_horizontal:
                    if abs(img_y / ph - self._split_pos) < 0.02:
                        self._split_dragging = True
                        return
                else:
                    if abs(img_x / pw - self._split_pos) < 0.02:
                        self._split_dragging = True
                        return
            self._dragging = True
            self._drag_start = (event.pos().x(), event.pos().y())
        elif event.button() == Qt.RightButton:
            self._fit_to_widget()
            self.update()

    def mouseMoveEvent(self, event):
        if self._split_dragging and self._pixmap:
            if self._split_horizontal:
                img_y = (event.pos().y() - self._pan_y) / self._zoom
                self._split_pos = max(0.05, min(0.95, img_y / self._pixmap.height()))
            else:
                img_x = (event.pos().x() - self._pan_x) / self._zoom
                self._split_pos = max(0.05, min(0.95, img_x / self._pixmap.width()))
            self.update()
            return
        if (self._shape_mode or self._region_mode) and self._shape_start and self._pixmap:
            img_x = (event.pos().x() - self._pan_x) / self._zoom
            img_y = (event.pos().y() - self._pan_y) / self._zoom
            self._shape_current = (img_x, img_y)
            self.update()
            return
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
        if self._shape_mode and self._shape_start and self._shape_current:
            sx, sy = self._shape_start
            cx, cy = self._shape_current
            if self._shape_mode == 'Circle':
                rx = abs(cx - sx)
                ry = abs(cy - sy)
                r = max(rx, ry)
                params = {'cx': int(sx), 'cy': int(sy), 'r': int(r)}
            else:
                x0, y0 = min(sx, cx), min(sy, cy)
                w, h = abs(cx - sx), abs(cy - sy)
                params = {'x0': int(x0), 'y0': int(y0), 'x1': int(x0 + w), 'y1': int(y0 + h)}
            self.shape_drawn.emit(self._shape_mode, params)
            self._shape_start = None
            self._shape_current = None
            self.update()
        elif self._region_mode and self._shape_start and self._shape_current:
            sx, sy = self._shape_start
            cx, cy = self._shape_current
            x0, y0 = min(sx, cx), min(sy, cy)
            w, h = abs(cx - sx), abs(cy - sy)
            if w > 5 and h > 5:
                pw = self._pixmap.width() if self._pixmap else 1
                ph = self._pixmap.height() if self._pixmap else 1
                fw = self._frame_array.shape[1] if self._frame_array is not None else pw
                fh = self._frame_array.shape[0] if self._frame_array is not None else ph
                fx0 = int(x0 * fw / pw)
                fy0 = int(y0 * fh / ph)
                fw_px = int(w * fw / pw)
                fh_px = int(h * fh / ph)
                self.region_selected.emit((fx0, fy0, fw_px, fh_px))
            self._shape_start = None
            self._shape_current = None
            self.update()
        self._dragging = False
        self._split_dragging = False

    def set_tracker_bbox(self, bbox):
        self._tracker_bbox = bbox
        self.update()

    def set_pipette_mode(self, enabled=True):
        self._pipette_mode = enabled
        if enabled:
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def set_shape_mode(self, mode):
        self._shape_mode = mode
        if mode:
            self._region_mode = False
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def set_region_mode(self, enabled=True):
        self._region_mode = enabled
        if enabled:
            self._shape_mode = None
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def set_split_horizontal(self, horizontal=True):
        self._split_horizontal = horizontal
        self.update()


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
        self.version_manager = VersionManager()
        self.current_frame = None
        self.original_frame = None
        self.current_project_path = None
        self.current_lut_path = None
        self._channel_visible = {'R': True, 'G': True, 'B': True, 'Alpha': True}
        self._pipette_active = False
        self._split_view = False
        self._grading_cache = GradingCache()
        self._preview_scale = 0.25
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
        self.viewer.shape_drawn.connect(self._on_shape_drawn)
        self.viewer.region_selected.connect(self._on_region_selected)
        v_layout.addWidget(self.viewer, 1)
        vt = QHBoxLayout()
        for text, slot in [("Fit", self._fit_viewer), ("1:1", self._zoom_100),
                           ("Split", self._toggle_split), ("H/V", self._toggle_split_orientation),
                           ("R", self._toggle_red), ("G", self._toggle_green),
                           ("B", self._toggle_blue), ("Alpha", self._toggle_alpha)]:
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
        for text, slot in [("CircleW", self._select_circle_window),
                           ("RectW", self._select_rect_window),
                           ("TrackR", self._select_track_region)]:
            btn = QPushButton(text)
            btn.setFixedHeight(24)
            btn.setCheckable(True)
            btn.setToolTip(text.replace("W", " Window").replace("R", " Region"))
            setattr(self, f'_ch_{text.lower()}', btn)
            btn.clicked.connect(slot)
            vt.addWidget(btn)
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
        right_tabs.addTab(self._build_versions_tab(), "Versions")
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
        self._build_color_slice_tab()
        self._build_color_warper_tab()
        self._build_power_windows_tab()
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
        self._scopes_tab_widget = scopes_and_info
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
        file_menu.addAction("Export Frame...", self._export_frame)
        file_menu.addAction("Batch Export...", self._batch_export)
        file_menu.addSeparator()
        self._recent_menu = file_menu.addMenu("Recent Files")
        self._refresh_recent()
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        edit_menu = mb.addMenu("Edit")
        edit_menu.addAction("Undo", self._undo).setShortcut(QKeySequence.Undo)
        edit_menu.addAction("Redo", self._redo).setShortcut(QKeySequence("Ctrl+Shift+Z"))
        edit_menu.addSeparator()
        edit_menu.addAction("Reset Grade", self._reset_grade)
        edit_menu.addAction("Reset All", self._reset_all)

        view_menu = mb.addMenu("View")
        self._show_scopes_action = view_menu.addAction("Show Scopes")
        self._show_scopes_action.setCheckable(True)
        self._show_scopes_action.setChecked(True)
        self._show_scopes_action.toggled.connect(self._toggle_scopes)
        view_menu.addAction("Before/After Split", self._toggle_split)

        grade_menu = mb.addMenu("Grade")
        grade_menu.addAction("Grab Still", self._grab_still)
        grade_menu.addAction("Apply Still to Current", self._apply_still_to_current)

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

        cs_row = QHBoxLayout()
        cs_row.addWidget(QLabel("Color Space:"))
        self._colorspace_combo = QComboBox()
        self._colorspace_combo.addItems([
            "sRGB", "Scene Linear", "Rec.709", "Rec.2020",
            "ACES AP0", "ACEScg", "P3-D65"
        ])
        self._colorspace_combo.currentTextChanged.connect(self._on_colorspace_changed)
        self._colorspace_combo.setFixedWidth(140)
        cs_row.addWidget(self._colorspace_combo)
        cs_row.addStretch()

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
        layout.addLayout(cs_row)
        self.palette_stack.addTab(tab, "Primaries")

    def _build_curves_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("RGB Curves"))
        from ui.widgets.curve_canvas import CurveCanvas
        self.curve_canvas = CurveCanvas()
        self.curve_canvas.setMinimumHeight(150)
        self.curve_canvas.curveChanged.connect(self._on_curve_changed)
        layout.addWidget(self.curve_canvas, 1)
        hsl_row = QHBoxLayout()
        for name in ["RGB", "R", "G", "B"]:
            btn = QPushButton(name)
            btn.setFixedHeight(24)
            btn.clicked.connect(lambda checked, n=name: self.curve_canvas.set_active_channel(n))
            hsl_row.addWidget(btn)
        reset_curve_btn = QPushButton("Reset")
        reset_curve_btn.setFixedHeight(24)
        reset_curve_btn.clicked.connect(self.curve_canvas.reset_current)
        hsl_row.addWidget(reset_curve_btn)
        layout.addLayout(hsl_row)
        self.palette_stack.addTab(tab, "Curves")

    def _build_keying_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Qualifier (Keying)"))
        key_row = QHBoxLayout()
        kb = QPushButton("Pick Key Color")
        kb.clicked.connect(self._pick_key_color)
        key_row.addWidget(kb)
        self._key_color_label = QLabel("None")
        self._key_color_label.setStyleSheet("color: #888; font-size: 11px;")
        key_row.addWidget(self._key_color_label)
        key_row.addStretch()
        layout.addLayout(key_row)
        self._key_sliders = {}
        for name, lo, hi, default in [
            ("Hue Range", 0, 180, 30),
            ("Sat Range", 0, 255, 60),
            ("Luma Range", 0, 255, 60),
            ("Softness", 0, 100, 20),
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(name))
            sl = QSlider(Qt.Horizontal)
            sl.setRange(lo, hi)
            sl.setValue(default)
            val_label = QLabel(str(default))
            val_label.setFixedWidth(40)
            key_name = name.lower().replace(' ', '_').replace('/', '_')
            def make_key_cb(k=key_name, vl=val_label):
                def cb(v):
                    vl.setText(str(v))
                    self._update_grade()
                return cb
            sl.valueChanged.connect(make_key_cb())
            row.addWidget(sl, 1)
            row.addWidget(val_label)
            layout.addLayout(row)
            self._key_sliders[key_name] = sl
        self._key_color = None
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
        fx_map = {
            "Blur": "blur", "Glow": "glow", "Sharpen": "sharpen",
            "Vignette": "vignette", "Film Grain": "film_grain",
            "Shadows/Highlights": "shadows_highlights",
            "Split Toning": "split_toning", "Color Temperature": "color_temperature",
            "Invert": "invert", "Posterize": "posterize", "Pixelate": "pixelate",
            "Tonemap": "tonemap",
        }
        for display_name, node_type in fx_map.items():
            btn = QPushButton(f"+ {display_name}")
            btn.setStyleSheet("""QPushButton { background-color: #333; color: #888; border: 1px solid #444;
                border-radius: 4px; padding: 6px 10px; font-size: 12px; text-align: left; }
                QPushButton:hover { background-color: #444; color: #aaa; }""")
            btn.clicked.connect(lambda checked, t=node_type, n=display_name: self._add_fx_node(t, n))
            layout.addWidget(btn)
        layout.addStretch()
        return tab

    def _build_versions_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Grade Versions"))
        self._versions_list = QListWidget()
        self._versions_list.setStyleSheet("""QListWidget { background-color: #222; border: 1px solid #333;
            border-radius: 4px; color: #888; font-size: 12px; }
            QListWidget::item:selected { background-color: #3a3a3a; color: #aaa; }""")
        self._versions_list.itemDoubleClicked.connect(self._on_version_selected)
        layout.addWidget(self._versions_list, 1)
        btn_row = QHBoxLayout()
        for text, cb in [("Add Version", self._add_version), ("Delete", self._delete_version),
                         ("Rename", self._rename_version)]:
            btn = QPushButton(text)
            btn.setStyleSheet("""QPushButton { background-color: #333; color: #888; border: 1px solid #444;
                border-radius: 4px; padding: 6px 12px; font-size: 12px; }
                QPushButton:hover { background-color: #444; color: #aaa; }""")
            btn.clicked.connect(cb)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)
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
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self._export_frame)
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(self._batch_export)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self._grab_still)

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

    def _on_curve_changed(self):
        self._push_undo()
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

    def _toggle_split(self):
        self._split_view = not self._split_view
        self.viewer.set_split_mode(self._split_view)
        if self._split_view and self.original_frame is not None:
            self.viewer.set_image_before(self.original_frame)
        self._update_grade()

    def _toggle_scopes(self, checked):
        self._scopes_tab_widget.setVisible(checked)

    def _toggle_split_orientation(self):
        new_val = not self.viewer._split_horizontal
        self.viewer.set_split_horizontal(new_val)
        self.status_label.setText(f"Split view: {'Horizontal' if new_val else 'Vertical'}")

    def _on_colorspace_changed(self, cs_name):
        cs_map = {
            "sRGB": "srgb", "Scene Linear": "scene_linear", "Rec.709": "rec709",
            "Rec.2020": "rec2020", "ACES AP0": "aces_ap0", "ACEScg": "acescg",
            "P3-D65": "p3d65",
        }
        cs_key = cs_map.get(cs_name, "srgb")
        self.app_state.colorspace = cs_key
        self._update_grade()
        self.status_label.setText(f"Color space: {cs_name}")

    def _select_circle_window(self):
        active = self.viewer._shape_mode != 'Circle'
        self.viewer.set_shape_mode('Circle' if active else None)
        self._ch_circlew.setChecked(active)

    def _select_rect_window(self):
        active = self.viewer._shape_mode != 'Rectangle'
        self.viewer.set_shape_mode('Rectangle' if active else None)
        self._ch_rectw.setChecked(active)

    def _select_track_region(self):
        active = not self.viewer._region_mode
        self.viewer.set_region_mode(active)
        self._ch_trackr.setChecked(active)

    def _on_shape_drawn(self, shape_type, params):
        self.power_windows.set_shape_params(shape_type, params)
        if not any(m['type'] == shape_type for m in self.power_windows._masks):
            self.power_windows._mask_list.addItem(shape_type)
            self.power_windows._masks.append({'type': shape_type, 'params': params})
        self.viewer.set_shape_mode(None)
        self._ch_circlew.setChecked(False)
        self._ch_rectw.setChecked(False)
        self._update_grade()
        self.status_label.setText(f"Drew {shape_type} power window")

    def _on_region_selected(self, bbox):
        self.tracker_panel.set_bbox(bbox)
        self.viewer.set_region_mode(False)
        self._ch_trackr.setChecked(False)
        self.status_label.setText(f"Tracking region selected: {bbox}")

    # ─── FX / Node Graph ───

    def _add_fx_node(self, node_type, display_name):
        from nodes import create_node
        node = create_node(node_type, display_name)
        self.node_graph.add_node(node)
        self.node_editor.rebuild()
        self._on_node_graph_changed()
        self.status_label.setText(f"Added node: {display_name}")

    def _pick_key_color(self):
        self._pipette_active = True
        self._pipette_btn.setChecked(True)
        self.viewer.set_pipette_mode(True)
        self.status_label.setText("Click on viewer to pick key color")

    def _on_color_picked(self, r, g, b):
        self._pipette_active = False
        self._pipette_btn.setChecked(False)
        self.viewer.set_pipette_mode(False)
        hsv = rgb_to_hsv(np.array([[[r, g, b]]]))[0, 0]
        self.info_panel.update_cursor_info({
            'position': 'Picked',
            'rgb': f"({r:.3f}, {g:.3f}, {b:.3f})",
            'hsv': f"({hsv[0]:.3f}, {hsv[1]:.3f}, {hsv[2]:.3f})",
        })
        if hasattr(self, '_key_color_label') and hasattr(self, '_pick_key_color'):
            self._key_color = (r, g, b)
            self._key_color_label.setText(f"({r:.2f}, {g:.2f}, {b:.2f})")
            self._key_color_label.setStyleSheet(
                f"color: rgb({int(r*255)},{int(g*255)},{int(b*255)}); font-size: 11px;")
            self._update_grade()
        self.status_label.setText(f"Color picked: RGB({r:.3f}, {g:.3f}, {b:.3f})")

    # ─── Versions ───

    def _add_version(self):
        name, ok = QInputDialog.getText(self, "New Version", "Version name:")
        if ok and name:
            idx = self.version_manager.add_version(
                name, self.grade_params, self.current_lut_path,
                self.node_graph.to_dict() if self.node_graph.nodes else None
            )
            self._refresh_versions_list()
            self.status_label.setText(f"Added version: {name}")

    def _delete_version(self):
        row = self._versions_list.currentRow()
        if row >= 0:
            self.version_manager.delete_version(row)
            self._refresh_versions_list()

    def _rename_version(self):
        row = self._versions_list.currentRow()
        if row >= 0:
            name, ok = QInputDialog.getText(self, "Rename Version", "New name:")
            if ok and name:
                self.version_manager.rename_version(row, name)
                self._refresh_versions_list()

    def _on_version_selected(self, item):
        row = self._versions_list.currentRow()
        v = self.version_manager.select_version(row)
        if v:
            self.grade_params.update(v.grade_params)
            if v.lut_path and os.path.exists(v.lut_path):
                lut = cube_to_lut3d(v.lut_path)
                if lut is not None:
                    self.lut = lut
                    self.current_lut_path = v.lut_path
            elif v.lut_path is None:
                self.lut = None
                self.current_lut_path = None
            if v.node_graph:
                self.node_graph = NodeGraph.from_dict(v.node_graph, NODE_CLASSES)
                self.node_editor.rebuild()
            self._update_grade()
            self.status_label.setText(f"Loaded version: {v.name}")

    def _refresh_versions_list(self):
        self._versions_list.clear()
        for v in self.version_manager.versions:
            self._versions_list.addItem(v.name)

    # ─── Gallery ───

    def _grab_still(self):
        if self.current_frame is None:
            return
        name = f"Still {len(self.gallery_panel._stills) + 1}"
        self.gallery_panel.add_still(name, self.current_frame, self.grade_params)
        self.status_label.setText(f"Grabbed still: {name}")

    def _apply_still_to_current(self):
        row = self.gallery_panel._stills_list.currentRow()
        if row >= 0:
            self.gallery_panel._on_load()

    # ─── Batch Export ───

    def _batch_export(self):
        from core.batch_export import BatchExportDialog
        dlg = BatchExportDialog(self._apply_grade_to_frame, self)
        dlg.exec()

    def _apply_grade_to_frame(self, frame: np.ndarray) -> np.ndarray:
        img = frame.copy()
        p = self.grade_params
        lift = p['lift']
        gamma_inv = [1.0 / max(p['gamma'][c], 0.001) for c in range(3)]
        gain = p['gain']
        if any(abs(lift[i]) > 1e-6 or abs(gamma_inv[i] - 1.0) > 1e-6 or abs(gain[i] - 1.0) > 1e-6 for i in range(3)):
            self._grading_cache.apply_lgg_inplace(img, lift, gamma_inv, gain)
        offset = p['offset']
        if any(abs(offset[i]) > 1e-6 for i in range(3)):
            img[..., :3] += np.asarray(offset)
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
        return np.clip(img, 0.0, 1.0)

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
            versions=self.version_manager.get_snapshot().get('versions'),
            version_index=self.version_manager.current_index,
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
        if project.versions:
            self.version_manager.load_snapshot({
                'versions': project.versions,
                'current_index': project.version_index,
            })
            self._refresh_versions_list()
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
                'bit_depth': f"{img.mode}",
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

    # ─── Grading Pipeline ───

    def _update_grade(self):
        if self.original_frame is None:
            return
        p = self.grade_params

        lift = p['lift']
        gamma_inv = [1.0 / max(p['gamma'][c], 0.001) for c in range(3)]
        gain = p['gain']
        has_lgg = any(abs(lift[i]) > 1e-6 or abs(gamma_inv[i] - 1.0) > 1e-6 or abs(gain[i] - 1.0) > 1e-6 for i in range(3))
        offset = p['offset']
        has_offset = any(abs(offset[i]) > 1e-6 for i in range(3))
        has_contrast = p['contrast'] != 0.0
        has_saturation = p['saturation'] != 0.0
        has_exposure = p['exposure'] != 0.0

        h, w = self.original_frame.shape[:2]
        scale = self._preview_scale if (has_lgg or has_saturation or has_contrast or has_exposure) else 1.0

        if scale < 1.0:
            sh = max(int(h * scale), 1)
            sw = max(int(w * scale), 1)
            img = self.original_frame[::max(int(1/scale), 1), ::max(int(1/scale), 1), :].copy()
        else:
            img = self.original_frame.copy()

        if has_lgg:
            self._grading_cache.apply_lgg_inplace(img, lift, gamma_inv, gain)

        if has_offset:
            img[..., :3] += np.asarray(offset)

        if has_contrast:
            img = apply_brightness_contrast(img, 0.0, p['contrast'])
        if has_saturation:
            luma = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
            f = p['saturation']
            img[..., 0] += f * (img[..., 0] - luma)
            img[..., 1] += f * (img[..., 1] - luma)
            img[..., 2] += f * (img[..., 2] - luma)
            np.clip(img, 0, 1, out=img)
        if has_exposure:
            np.multiply(img, np.float32(2.0 ** p['exposure']), out=img)

        if self.lut is not None:
            img = apply_lut_3d(img, self.lut)

        if hasattr(self, 'curve_canvas') and self.curve_canvas is not None:
            curves = self.curve_canvas.get_all_curves()
            has_custom = False
            for ch, pts in curves.items():
                if len(pts) > 2 or (len(pts) == 2 and pts != [(0.0, 0.0), (1.0, 1.0)]):
                    has_custom = True
                    break
            if has_custom:
                img = node_rgb_curves(img, curves=curves)

        if hasattr(self, 'color_slice') and self.color_slice is not None:
            img = self.color_slice.apply_to_image(img)

        if hasattr(self, 'color_warper') and self.color_warper is not None:
            grid = self.color_warper._grid
            is_identity = True
            n = len(grid)
            for i in range(n):
                for j in range(n):
                    expected = [j / max(n - 1, 1), i / max(n - 1, 1)]
                    if abs(grid[i][j][0] - expected[0]) > 0.01 or abs(grid[i][j][1] - expected[1]) > 0.01:
                        is_identity = False
                        break
                if not is_identity:
                    break
            if not is_identity:
                img = apply_color_warp(img, grid)

        if self.node_graph.nodes:
            self.node_graph.mark_all_dirty()
            result = self.node_graph.execute(img)
            if result is not None:
                img = result

        if hasattr(self, '_key_color') and self._key_color is not None and hasattr(self, '_key_sliders'):
            hue_range = self._key_sliders.get('hue_range', None)
            if hue_range is not None:
                kr, kg, kb = self._key_color
                hsv_img = rgb_to_hsv(np.clip(img[..., :3], 0, 1))
                key_hsv = rgb_to_hsv(np.array([[[kr, kg, kb]]]))[0, 0]
                hue_diff = np.abs(hsv_img[..., 0] - key_hsv[0])
                hue_diff = np.minimum(hue_diff, 1.0 - hue_diff)
                hue_mask = np.clip(1.0 - hue_diff / max(hue_range.value() / 180.0, 0.01), 0, 1)
                sat_range = self._key_sliders.get('sat_range', None)
                if sat_range is not None:
                    sat_diff = np.abs(hsv_img[..., 1] - key_hsv[1])
                    sat_mask = np.clip(1.0 - sat_diff / max(sat_range.value() / 255.0, 0.01), 0, 1)
                    hue_mask *= sat_mask
                softness = self._key_sliders.get('softness', None)
                if softness is not None:
                    s = softness.value() / 100.0
                    hue_mask = np.clip(hue_mask * (1.0 + s), 0, 1)
                mask = hue_mask
                if hasattr(self, '_key_inverted') and self._key_inverted:
                    mask = 1.0 - mask

        if hasattr(self, 'power_windows') and self.power_windows is not None:
            mask = self.power_windows.render_mask(img.shape[1], img.shape[0])
            if mask is not None and mask.max() > 0:
                img = img * (1.0 - mask[:, :, None]) + self.original_frame * mask[:, :, None]

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

        if self._split_view and self.original_frame is not None:
            if scale < 1.0:
                sh = max(int(h * scale), 1)
                sw = max(int(w * scale), 1)
                before = self.original_frame[::max(int(1/scale), 1), ::max(int(1/scale), 1), :]
            else:
                before = self.original_frame
            self.viewer.set_image_before(before)
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
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Frame", "",
            "PNG (*.png);;JPEG (*.jpg);;TIFF (*.tif);;EXR (*.exr)")
        if path:
            from PIL import Image
            arr = np.clip(self.current_frame * 255.0, 0, 255).astype(np.uint8)
            Image.fromarray(arr).save(path)
            self.status_label.setText(f"Exported: {os.path.basename(path)}")

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
        self._key_color = None
        if hasattr(self, 'curve_canvas'):
            self.curve_canvas.reset_all()
        if self.original_frame is not None:
            self.current_frame = self.original_frame.copy()
            self.viewer.set_image(self.current_frame)

    def _on_node_graph_changed(self):
        self._push_undo()
        self._update_grade()
