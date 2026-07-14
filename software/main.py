#!/usr/bin/env python3
"""davici-resolve — Professional Color Grading Panel
Ported from Blender's GPL compositor nodes color science.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("davici-resolve")
    app.setOrganizationName("davici")
    app.setWindowIcon(QIcon())

    from ui.theme.dark_theme import apply_dark_theme
    apply_dark_theme(app)

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
