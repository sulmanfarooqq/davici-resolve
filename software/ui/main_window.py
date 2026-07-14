"""Main window — DaVinci Resolve Color Page style layout."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QPushButton, QLabel, QSlider, QFileDialog,
    QMenuBar, QToolBar, QStatusBar, QDockWidget, QScrollArea,
    QFrame, QGraphicsView, QGraphicsScene, QMessageBox, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QImage, QPixmap, QPainter, QColor, QPen
import numpy as np
import os

from ui.app_state import AppState
from core.video_io import VideoReader
from core.frame_cache import FrameCache
from core.color_math import (
    colorbalance_lgg, apply_brightness_contrast, apply_saturation,
    apply_exposure, apply_gamma, apply_invert
)
from core.lut_parser import parse_cube, cube_to_lut3d, apply_lut_3d


class ViewerGL(QWidget):
    """Simple image viewer with zoom/pan."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #000000;")
        self._pixmap = None
        self._zoom = 1.0
        self._pan_x = 0
        self._pan_y = 0
        self._dragging = False
        self._drag_start = None

    def set_image(self, rgb_array: np.ndarray):
        if rgb_array is None:
            self._pixmap = None
            self.update()
            return
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
            painter.restore()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        factor = 1.1 if delta > 0 else 0.9
        self._zoom *= factor
        self._zoom = max(0.05, min(self._zoom, 50.0))
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
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

    def mouseReleaseEvent(self, event):
        self._dragging = False


class ColorWheelWidget(QWidget):
    """Circular color wheel with draggable puck."""

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

    def set_value(self, x: float, y: float):
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
        # Color wheel segments
        segments = 64
        for i in range(segments):
            a1 = (i / segments) * 6.2832
            a2 = ((i + 1) / segments) * 6.2832
            h = i / segments
            h6 = h * 6.0
            hi = int(h6)
            f = h6 - hi
            if hi == 0: rgb = (1.0, f, 0.0)
            elif hi == 1: rgb = (1.0 - f, 1.0, 0.0)
            elif hi == 2: rgb = (0.0, 1.0, f)
            elif hi == 3: rgb = (0.0, 1.0 - f, 1.0)
            elif hi == 4: rgb = (f, 0.0, 1.0)
            else: rgb = (1.0, 0.0, 1.0 - f)
            color = QColor(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawPie(cx - r, cy - r, r*2, r*2,
                          int(a1 * 5760 / 3.14159), int((a2 - a1) * 5760 / 3.14159))
        # Brightness overlay
        for i in range(8):
            t = i / 8
            alpha = int(100 * (1 - t))
            ir = r * t
            painter.setBrush(QColor(0, 0, 0, alpha))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx - ir, cy - ir, ir*2, ir*2)
        # Outer ring
        painter.setPen(QPen(QColor("#555"), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(cx - r, cy - r, r*2, r*2)
        # Puck
        px = cx + self._value[0] * r * 0.7
        py = cy + self._value[1] * r * 0.7
        pr = 5
        painter.setPen(QPen(QColor("#333"), 1))
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(px - pr, py - pr, pr*2, pr*2)
        # Label
        painter.setPen(QColor("#888"))
        painter.drawText(0, self._size + 15, self._size + 20, 15,
                        Qt.AlignCenter, self.label)

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
        self.current_frame = None
        self.original_frame = None
        self.grade_params = {
            'lift': [0.0, 0.0, 0.0],
            'gamma': [1.0, 1.0, 1.0],
            'gain': [1.0, 1.0, 1.0],
            'offset': [0.0, 0.0, 0.0],
            'contrast': 0.0,
            'saturation': 0.0,
            'exposure': 0.0,
            'temp': 0.0,
            'tint': 0.0,
        }
        self.lut = None
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

        # Top splitter: Viewer + Right panels
        top_split = QSplitter(Qt.Horizontal)
        main_layout.addWidget(top_split, 1)

        # Viewer
        viewer_container = QWidget()
        v_layout = QVBoxLayout(viewer_container)
        v_layout.setContentsMargins(2, 2, 2, 2)
        v_layout.setSpacing(2)
        self.viewer = ViewerGL()
        v_layout.addWidget(self.viewer, 1)
        # Viewer toolbar
        vt = QHBoxLayout()
        for text, slot in [("Fit", self._fit_viewer), ("1:1", self._zoom_100),
                           ("R", lambda: None), ("G", lambda: None), ("B", lambda: None)]:
            btn = QPushButton(text)
            btn.setFixedHeight(24)
            btn.clicked.connect(slot)
            vt.addWidget(btn)
        v_layout.addLayout(vt)
        top_split.addWidget(viewer_container)

        # Right panel: tabs for Node Editor + Open FX
        right_tabs = QTabWidget()
        right_tabs.setMinimumWidth(280)
        right_tabs.addTab(self._build_node_editor_tab(), "Node Editor")
        right_tabs.addTab(self._build_fx_tab(), "Open FX")
        top_split.addWidget(right_tabs)
        top_split.setSizes([800, 300])

        # Bottom area: palette bar + scopes
        bottom_widget = QWidget()
        b_layout = QVBoxLayout(bottom_widget)
        b_layout.setContentsMargins(0, 0, 0, 0)
        b_layout.setSpacing(0)

        # Palette button bar
        self._build_palette_bar(b_layout)

        # Splitter: active palette + scopes
        pal_scope_split = QSplitter(Qt.Horizontal)
        b_layout.addWidget(pal_scope_split, 1)

        # Active palette area
        self.palette_stack = QTabWidget()
        self.palette_stack.setMinimumHeight(150)
        self._build_primaries_tab()
        self._build_curves_tab()
        self._build_keying_tab()
        self.palette_stack.setCurrentIndex(0)
        pal_scope_split.addWidget(self.palette_stack)

        # Scopes panel
        self.scopes_tabs = QTabWidget()
        self.scopes_tabs.setMinimumWidth(300)
        self.scope_waveform = ViewerGL()
        self.scope_histogram = ViewerGL()
        self.scopes_tabs.addTab(self.scope_waveform, "Waveform")
        self.scopes_tabs.addTab(self.scope_histogram, "Histogram")
        pal_scope_split.addWidget(self.scopes_tabs)
        pal_scope_split.setSizes([500, 350])

        main_layout.addWidget(bottom_widget, 0)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("No image loaded")
        self.status_bar.addWidget(self.status_label)

        # Scopes update timer
        self._scope_timer = QTimer()
        self._scope_timer.timeout.connect(self._update_scopes)
        self._scope_timer.start(200)

    def _build_menubar(self):
        mb = self.menuBar()
        file_menu = mb.addMenu("File")
        for text, cb in [("Open Image...", self._open_image),
                         ("Open LUT...", self._open_lut),
                         (None, None),
                         ("Export Frame...", self._export_frame),
                         (None, None),
                         ("Exit", self.close)]:
            if text is None:
                file_menu.addSeparator()
            else:
                file_menu.addAction(text, cb)
        edit_menu = mb.addMenu("Edit")
        edit_menu.addAction("Reset Grade", self._reset_grade)
        edit_menu.addAction("Reset All", self._reset_all)
        view_menu = mb.addMenu("View")
        self._show_scopes_action = view_menu.addAction("Scopes")
        self._show_scopes_action.setCheckable(True)
        self._show_scopes_action.setChecked(True)

    def _build_toolbar(self):
        tb = QToolBar("Transport")
        tb.setIconSize(tb.iconSize())
        self.addToolBar(tb)

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
        self.palette_stack.setCurrentIndex(idx)

    def _build_primaries_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # 4 color wheels
        wheels_frame = QWidget()
        wl = QVBoxLayout(wheels_frame)

        def make_wheel(label, key):
            w = ColorWheelWidget(label=label, size=60)
            def on_change(val):
                self.grade_params[key][0] = val[0]
                self.grade_params[key][1] = val[1]
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

        # Sliders
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
            label = QLabel(name)
            label.setFixedWidth(80)
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
                    self._update_grade()
                return cb
            slider.valueChanged.connect(make_cb())
            row.addWidget(label)
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
        self.curve_canvas = ViewerGL()
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
        # Key color picker placeholder
        kb = QPushButton("Pick Key Color")
        layout.addWidget(kb)
        for name in ["Hue Range", "Sat Range", "Luma Range"]:
            row = QHBoxLayout()
            row.addWidget(QLabel(name))
            sl = QSlider(Qt.Horizontal)
            row.addWidget(sl)
            layout.addLayout(row)
        self.palette_stack.addTab(tab, "Keying")

    def _build_node_editor_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.node_scene = QGraphicsScene()
        self.node_view = QGraphicsView(self.node_scene)
        self.node_view.setStyleSheet("background-color: #1a1a1e;")
        layout.addWidget(self.node_view, 1)
        btn_row = QHBoxLayout()
        for text in ["Add Node", "Bypass", "Reset"]:
            btn_row.addWidget(QPushButton(text))
        layout.addLayout(btn_row)
        return tab

    def _build_fx_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Open FX Browser"))
        for name in ["Blur", "Glow", "Sharpen", "Vignette", "Film Grain"]:
            layout.addWidget(QPushButton(name))
        layout.addStretch()
        return tab

    def _setup_shortcuts(self):
        from PySide6.QtGui import QShortcut, QKeySequence
        shortcuts = [
            ("Ctrl+O", self._open_image), ("Ctrl+L", self._open_lut),
            ("Ctrl+Q", self.close), ("Ctrl+R", self._reset_grade),
        ]
        for seq, cb in shortcuts:
            QShortcut(QKeySequence(seq), self).activated.connect(cb)

    # ─── Image operations ───

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
            self._update_grade()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _open_lut(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open LUT", "", "Cube LUT (*.cube)")
        if not path:
            return
        lut = cube_to_lut3d(path)
        if lut is not None:
            self.lut = lut
            self.status_label.setText(f"LUT loaded: {os.path.basename(path)}")
            self._update_grade()
        else:
            QMessageBox.warning(self, "Error", "Invalid 3D LUT")

    def _update_grade(self):
        if self.original_frame is None:
            return
        img = self.original_frame.copy()
        p = self.grade_params
        # LGG
        img = img.astype(np.float32)
        for c in range(3):
            l = p['lift'][c]
            g = 1.0 / max(p['gamma'][c], 0.001)
            gn = p['gain'][c]
            img[:,:,c] = colorbalance_lgg(img[:,:,c], l, g, gn)
        img[:,:,:3] += np.array(p['offset'])
        # Contrast, saturation, exposure
        if p['contrast'] != 0.0:
            img = apply_brightness_contrast(img, 0.0, p['contrast'])
        if p['saturation'] != 0.0:
            img = apply_saturation(img, p['saturation'])
        if p['exposure'] != 0.0:
            img = apply_exposure(img, p['exposure'])
        # LUT
        if self.lut is not None:
            lut_result = apply_lut_3d(img, self.lut)
            img = lut_result
        self.current_frame = np.clip(img, 0.0, 1.0)
        self.viewer.set_image(self.current_frame)

    def _update_scopes(self):
        if self.current_frame is None:
            return
        # Waveform
        w, h = 320, 120
        luma = 0.2126 * self.current_frame[:,:,0] + 0.7152 * self.current_frame[:,:,1] + 0.0722 * self.current_frame[:,:,2]
        scope = np.zeros((h, w, 3), dtype=np.uint8)
        step = max(1, luma.shape[0] // h)
        for y in range(0, luma.shape[0], step):
            row = luma[y, :]
            for x in range(0, len(row), 3):
                l_val = row[x]
                px = int(x / len(row) * (w - 4) + 2)
                py = int((h - 4) - l_val * (h - 8))
                if 0 <= px < w and 0 <= py < h:
                    scope[py, px] = [127, 255, 0]
        # Grid
        for i in range(5):
            gy = int(i * h / 4)
            scope[gy, :] = [42, 42, 42]
        self.scope_waveform.set_image(scope.astype(np.float32) / 255.0)
        # Histogram
        hist_img = np.zeros((h, w, 3), dtype=np.uint8)
        bins = w
        for ch in range(3):
            data = (self.current_frame[:,:,ch] * 255).ravel().astype(np.uint8)
            hist = np.bincount(data, minlength=256)[:bins]
            hist = hist[:bins]
            hist = np.log1p(hist.astype(np.float32) * 1000)
            mx = hist.max()
            if mx > 0:
                hist = hist / mx
            for i in range(bins):
                bh = int(hist[i] * (h - 4))
                color = [(255, 68, 68), (68, 255, 68), (68, 68, 255)][ch]
                for j in range(bh):
                    if h - 4 - j >= 0:
                        hist_img[h - 4 - j, i] = color
        self.scope_histogram.set_image(hist_img.astype(np.float32) / 255.0)

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
            'lift': [0.0, 0.0, 0.0],
            'gamma': [1.0, 1.0, 1.0],
            'gain': [1.0, 1.0, 1.0],
            'offset': [0.0, 0.0, 0.0],
            'contrast': 0.0,
            'saturation': 0.0,
            'exposure': 0.0,
            'temp': 0.0,
            'tint': 0.0,
        }
        self.lift_wheel.reset()
        self.gamma_wheel.reset()
        self.gain_wheel.reset()
        self.offset_wheel.reset()
        for key, slider in self._sliders.items():
            slider.setValue(0)
        self._update_grade()

    def _reset_all(self):
        self._reset_grade()
        self.lut = None
        if self.original_frame is not None:
            self.current_frame = self.original_frame.copy()
            self.viewer.set_image(self.current_frame)
