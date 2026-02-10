import logging

from PyQt5.QtWidgets import (QStatusBar, QLabel, QProgressBar, QWidget,
                             QHBoxLayout, QToolButton)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from ..utils.constants import LIGHT_THEME, DARK_THEME
from ..utils.helpers import load_icon, load_themed_icon
from ..utils.i18n import _ as tr

log = logging.getLogger(__name__)


class StatusBar(QStatusBar):
    zoom_clicked = pyqtSignal()
    ad_blocker_clicked = pyqtSignal()

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        self.setFixedHeight(28)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()

        self.url_label = QLabel()
        self.url_label.setMaximumWidth(600)

        self.zoom_btn = QToolButton()
        self.zoom_btn.setText("100%")
        self.zoom_btn.setFixedWidth(50)
        self.zoom_btn.clicked.connect(self.zoom_clicked.emit)
        self.zoom_btn.setToolTip(tr("Reset zoom"))

        self.security_label = QLabel()
        self.security_label.setFixedSize(20, 20)
        self.security_label.setPixmap(load_themed_icon("lock.svg", self.dark_mode).pixmap(14, 14))
        self.security_label.setToolTip(tr("Secure connection (HTTPS)"))

        self.ad_block_btn = QToolButton()
        self.ad_block_btn.setIcon(load_themed_icon("shield.svg", self.dark_mode))
        self.ad_block_btn.setIconSize(QSize(14, 14))
        self.ad_block_btn.setText(" 0")
        self.ad_block_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.ad_block_btn.clicked.connect(self.ad_blocker_clicked.emit)
        self.ad_block_btn.setToolTip(tr("Blocked ads count"))

        self.download_label = QLabel()
        self.download_label.hide()

        self.addWidget(self.progress_bar)
        self.addWidget(self.url_label, 1)
        self.addPermanentWidget(self.download_label)
        self.addPermanentWidget(self.ad_block_btn)
        self.addPermanentWidget(self.security_label)
        self.addPermanentWidget(self.zoom_btn)

    def _apply_style(self):
        theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        self.setStyleSheet(f"""
            QStatusBar {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_secondary']};
                border-top: 1px solid {theme['border']};
                font-size: 12px;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: {theme['bg_tertiary']};
            }}
            QProgressBar::chunk {{
                background-color: {theme['accent']};
                border-radius: 3px;
            }}
            QToolButton {{
                background: transparent;
                border: none;
                padding: 2px 6px;
                color: {theme['text_secondary']};
                border-radius: 3px;
                font-size: 12px;
            }}
            QToolButton:hover {{
                background-color: {theme['bg_tertiary']};
            }}
            QLabel {{
                color: {theme['text_secondary']};
                padding: 0 4px;
            }}
        """)

    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
        self._apply_style()
        self._update_icons()

    def _update_icons(self):
        self.security_label.setPixmap(load_themed_icon("lock.svg", self.dark_mode).pixmap(14, 14))
        self.ad_block_btn.setIcon(load_themed_icon("shield.svg", self.dark_mode))

    def show_progress(self, progress):
        if 0 < progress < 100:
            self.progress_bar.show()
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.hide()

    def hide_progress(self):
        self.progress_bar.hide()

    def set_url_text(self, text):
        self.url_label.setText(text)

    def clear_url_text(self):
        self.url_label.clear()

    def set_zoom(self, percentage):
        self.zoom_btn.setText(f"{percentage}%")

    def set_security(self, is_secure):
        if is_secure:
            self.security_label.setPixmap(load_icon("lock.svg", "#34a853").pixmap(14, 14))
            self.security_label.setToolTip(tr("Secure connection (HTTPS)"))
        else:
            self.security_label.setPixmap(load_icon("unlock.svg", "#ea4335").pixmap(14, 14))
            self.security_label.setToolTip(tr("Insecure connection"))

    def set_blocked_count(self, count):
        self.ad_block_btn.setText(f" {count}")

    def show_download_status(self, text):
        self.download_label.setText(text)
        self.download_label.show()

    def hide_download_status(self):
        self.download_label.hide()

    def show_message(self, message, timeout=3000):
        self.showMessage(message, timeout)
