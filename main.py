#!/usr/bin/env python3

import sys
import os
import logging

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QFont, QIcon

from browser.utils.i18n import set_language
from browser.ui.main_window import MainWindow
from browser.utils.constants import APP_NAME, APP_ORGANIZATION, APP_VERSION
from browser.utils.helpers import get_resource_path

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def main():
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORGANIZATION)

    # Initialize i18n from saved settings
    from browser.core.settings_manager import SettingsManager
    settings_mgr = SettingsManager()
    set_language(settings_mgr.language)

    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    icon_path = get_resource_path("icons", "globe.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
