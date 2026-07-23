"""Build a standalone .exe for davici-resolve using PyInstaller.
Run: python build_exe.py
Generated: dist/davici-resolve.exe
"""

import os, sys, subprocess, shutil

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    dist = os.path.join(base, "dist")
    spec_path = os.path.join(base, "davici-resolve.spec")

    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        import PyInstaller

    print("Building davici-resolve.exe...")
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "davici-resolve",
        "--icon", os.path.join(base, "icon.ico") if os.path.exists(os.path.join(base, "icon.ico")) else "",
        "--add-data", f"{base}{os.pathsep}.",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "PySide6.QtOpenGL",
        "--hidden-import", "cv2",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "numpy",
        "--hidden-import", "core.color_math",
        "--hidden-import", "core.video_io",
        "--hidden-import", "core.lut_parser",
        "--hidden-import", "core.project",
        "--hidden-import", "core.undo_manager",
        "--hidden-import", "core.node_graph",
        "--hidden-import", "core.frame_cache",
        "--hidden-import", "core.playback_controller",
        "--hidden-import", "nodes",
        "--hidden-import", "ui.main_window",
        "--hidden-import", "ui.app_state",
        "--hidden-import", "ui.theme.dark_theme",
        "--hidden-import", "ui.panels.info_panel",
        "--hidden-import", "ui.panels.color_slice",
        "--hidden-import", "ui.panels.color_warper",
        "--hidden-import", "ui.panels.power_windows",
        "--hidden-import", "ui.panels.tracker",
        "--hidden-import", "ui.panels.gallery",
        "--hidden-import", "ui.panels.lut_browser",
        "--hidden-import", "ui.widgets.transport_bar",
        "--hidden-import", "ui.widgets.timeline_widget",
        "--hidden-import", "ui.widgets.node_editor",
        "--hidden-import", "ui.widgets.scope_gl",
        "--hidden-import", "ui.widgets.curve_canvas",
        os.path.join(base, "main.py"),
    ])

    exe = os.path.join(dist, "davici-resolve.exe")
    if os.path.exists(exe):
        print(f"SUCCESS: {exe}")
        print(f"Size: {os.path.getsize(exe) / 1024 / 1024:.1f} MB")
    else:
        print("BUILD FAILED: exe not found at", exe)

if __name__ == "__main__":
    main()
