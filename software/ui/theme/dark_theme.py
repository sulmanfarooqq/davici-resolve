"""Dark theme matching DaVinci Resolve color page.
QPalette + QSS based on: planning/09_UI_DESIGN_SPEC.md
"""

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication


DARK_BG = "#1a1a1e"
PANEL_BG = "#222226"
PANEL_HEADER = "#2a2a2e"
WIDGET_BG = "#2c2c30"
HOVER_BG = "#3a3a3e"
SELECTED_BG = "#444448"
ACCENT = "#3498db"
ACCENT_HOVER = "#5dade2"
TEXT_PRIMARY = "#cccccc"
TEXT_SECONDARY = "#888888"
TEXT_DISABLED = "#555555"
SCOPE_BG = "#0d0d0d"


def apply_dark_theme(app: QApplication):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(DARK_BG))
    palette.setColor(QPalette.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Base, QColor(PANEL_BG))
    palette.setColor(QPalette.AlternateBase, QColor(PANEL_HEADER))
    palette.setColor(QPalette.ToolTipBase, QColor(PANEL_HEADER))
    palette.setColor(QPalette.ToolTipText, QColor("#ffffff"))
    palette.setColor(QPalette.Text, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Button, QColor(WIDGET_BG))
    palette.setColor(QPalette.ButtonText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    app.setStyleSheet("""
    QMainWindow { background-color: """ + DARK_BG + """; }
    QDockWidget { background-color: """ + PANEL_BG + """; }
    QDockWidget::title {
        background-color: """ + PANEL_HEADER + """;
        padding: 4px 8px;
        font-size: 11px; font-weight: bold;
        color: """ + TEXT_SECONDARY + """;
    }
    QMenuBar { background-color: """ + DARK_BG + """; color: """ + TEXT_PRIMARY + """; font-size: 12px; }
    QMenuBar::item:selected { background-color: """ + PANEL_HEADER + """; }
    QMenu { background-color: """ + PANEL_HEADER + """; border: 1px solid #555; }
    QMenu::item:selected { background-color: """ + HOVER_BG + """; }
    QToolBar { background-color: """ + PANEL_BG + """; border: none; spacing: 2px; }
    QStatusBar { background-color: """ + DARK_BG + """; color: """ + TEXT_SECONDARY + """; font-size: 11px; }
    QPushButton {
        background-color: """ + WIDGET_BG + """;
        color: """ + TEXT_PRIMARY + """;
        border: 1px solid #444;
        border-radius: 3px;
        padding: 4px 10px;
        font-size: 11px;
    }
    QPushButton:hover { background-color: """ + HOVER_BG + """; }
    QPushButton:pressed { background-color: """ + SELECTED_BG + """; }
    QPushButton:checked { background-color: """ + ACCENT + """; color: #ffffff; border-color: """ + ACCENT + """; }
    QSlider::groove:horizontal {
        height: 4px; background: """ + HOVER_BG + """;
        border-radius: 2px;
    }
    QSlider::handle:horizontal {
        width: 12px; height: 16px;
        background: #888; border-radius: 2px;
        margin: -6px 0;
    }
    QSlider::handle:horizontal:hover { background: """ + TEXT_PRIMARY + """; }
    QComboBox {
        background-color: """ + WIDGET_BG + """;
        color: """ + TEXT_PRIMARY + """;
        border: 1px solid #444;
        border-radius: 3px;
        padding: 2px 8px;
        font-size: 11px;
    }
    QComboBox:hover { border-color: #888; }
    QTabWidget::pane { background-color: """ + PANEL_BG + """; border: none; }
    QTabBar::tab {
        background-color: """ + PANEL_HEADER + """;
        color: """ + TEXT_SECONDARY + """;
        border: none; padding: 4px 12px; font-size: 11px;
    }
    QTabBar::tab:selected { background-color: """ + ACCENT + """; color: #ffffff; }
    QTabBar::tab:hover:!selected { background-color: """ + HOVER_BG + """; }
    QScrollBar:vertical {
        width: 8px; background: """ + DARK_BG + """;
    }
    QScrollBar::handle:vertical {
        background: """ + HOVER_BG + """;
        border-radius: 4px; min-height: 30px;
    }
    QScrollBar::handle:vertical:hover { background: """ + SELECTED_BG + """; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QLineEdit {
        background-color: """ + WIDGET_BG + """;
        color: """ + TEXT_PRIMARY + """;
        border: 1px solid #444; border-radius: 2px;
        padding: 2px 6px; font-size: 11px;
    }
    QLineEdit:focus { border-color: """ + ACCENT + """; }
    QToolTip {
        background-color: """ + PANEL_HEADER + """;
        color: #ffffff; border: 1px solid #444;
        padding: 4px 8px; font-size: 11px;
    }
    QSplitter::handle { background-color: """ + DARK_BG + """; width: 4px; }
    QSplitter::handle:hover { background-color: """ + ACCENT + """; }
    """)
