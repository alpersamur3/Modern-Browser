#!/usr/bin/env python3
"""
Modern Browser - Gelişmiş Web Tarayıcısı
=========================================

Modern, hızlı ve güvenli bir web tarayıcısı.

Özellikler:
- Sekmeli tarama
- Yer imleri yönetimi
- İndirme yöneticisi
- Gizli gezinti modu
- Karanlık mod
- Sayfa içi arama
- Zoom kontrolü
- Tam ekran modu
- Geçmiş yönetimi
- Reklam engelleyici
- Okuma modu
- Ekran görüntüsü
- Ve daha fazlası...

Kullanım:
    python main.py

Copyright (c) 2025 Alper Samur
MIT License
"""

import sys
import os

# Add browser package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QFont

from browser.ui.main_window import MainWindow
from browser.utils.constants import APP_NAME, APP_ORGANIZATION, APP_VERSION


def main():
    """Main entry point"""
    
    # High DPI support
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application info
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORGANIZATION)
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
