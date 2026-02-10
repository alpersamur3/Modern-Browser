from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QCheckBox,
                             QTabWidget, QWidget, QFormLayout,
                             QGroupBox, QFileDialog, QFrame, QToolButton)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont
from ..utils.constants import (LIGHT_THEME, DARK_THEME, SEARCH_ENGINES,
                               SUPPORTED_LANGUAGES, APP_NAME, APP_VERSION)
from ..utils.helpers import load_icon, load_themed_icon
from ..utils.i18n import _ as tr, get_available_languages


class BaseDialog(QDialog):
    def __init__(self, parent=None, title="", dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.setWindowTitle(title)
        self.setModal(True)
        self._apply_base_style()

    def _apply_base_style(self):
        theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_primary']};
                color: {theme['text_primary']};
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}
            QLabel {{
                color: {theme['text_primary']};
            }}
            QLineEdit, QTextEdit, QComboBox, QSpinBox {{
                background-color: {theme['bg_secondary']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {theme['text_primary']};
                font-size: 13px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {theme['accent']};
            }}
            QPushButton {{
                background-color: {theme['bg_tertiary']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 8px 20px;
                color: {theme['text_primary']};
                min-width: 80px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {theme['accent']};
                color: white;
                border-color: {theme['accent']};
            }}
            QPushButton:pressed {{
                background-color: {theme['accent_hover']};
            }}
            QPushButton#primaryBtn {{
                background-color: {theme['accent']};
                color: white;
                border-color: {theme['accent']};
            }}
            QPushButton#primaryBtn:hover {{
                background-color: {theme['accent_hover']};
            }}
            QPushButton#dangerBtn {{
                background-color: {theme['error']};
                color: white;
                border-color: {theme['error']};
            }}
            QGroupBox {{
                border: 1px solid {theme['border']};
                border-radius: 10px;
                margin-top: 18px;
                padding: 18px 12px 12px 12px;
                font-weight: bold;
                color: {theme['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 8px;
            }}
            QCheckBox {{
                color: {theme['text_primary']};
                spacing: 8px;
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {theme['border']};
                background: {theme['bg_secondary']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme['accent']};
                border-color: {theme['accent']};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme['border']};
                border-radius: 10px;
                background-color: {theme['bg_primary']};
            }}
            QTabBar::tab {{
                background-color: {theme['bg_secondary']};
                border: none;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                color: {theme['text_secondary']};
            }}
            QTabBar::tab:selected {{
                background-color: {theme['bg_primary']};
                color: {theme['accent']};
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {theme['bg_tertiary']};
            }}
        """)


class BookmarkDialog(BaseDialog):
    saved = pyqtSignal(str, str, str)

    def __init__(self, parent=None, title="", url="", folder="bookmarks_bar", dark_mode=False):
        super().__init__(parent, tr("Add Bookmark"), dark_mode)
        self.setFixedSize(420, 220)
        self._setup_ui(title, url)

    def _setup_ui(self, title, url):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel(f"{tr('Title')}:"))
        self.title_input = QLineEdit(title)
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)

        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel(f"{tr('URL')}:"))
        self.url_input = QLineEdit(url)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel(f"{tr('Folder')}:"))
        self.folder_combo = QComboBox()
        self.folder_combo.addItems([tr("Bookmarks Bar"), tr("Other Bookmarks")])
        folder_layout.addWidget(self.folder_combo)
        layout.addLayout(folder_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton(tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        save_btn = QPushButton(tr("Save"))
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._on_save)
        save_btn.setDefault(True)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _on_save(self):
        folder_map = {tr("Bookmarks Bar"): "bookmarks_bar", tr("Other Bookmarks"): "other_bookmarks"}
        folder = folder_map.get(self.folder_combo.currentText(), "bookmarks_bar")
        self.saved.emit(self.title_input.text(), self.url_input.text(), folder)
        self.accept()


class FindDialog(BaseDialog):
    find_requested = pyqtSignal(str, bool, bool)
    find_next = pyqtSignal()
    find_prev = pyqtSignal()
    closed = pyqtSignal()

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent, tr("Find in Page"), dark_mode)
        self.setFixedSize(440, 120)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("Search..."))
        self.search_input.textChanged.connect(self._on_text_changed)
        self.search_input.returnPressed.connect(self.find_next.emit)
        search_layout.addWidget(self.search_input)

        prev_btn = QToolButton()
        prev_btn.setIcon(load_themed_icon("chevrons-left.svg", self.dark_mode))
        prev_btn.setIconSize(QSize(16, 16))
        prev_btn.setFixedSize(32, 32)
        prev_btn.clicked.connect(self.find_prev.emit)
        search_layout.addWidget(prev_btn)

        next_btn = QToolButton()
        next_btn.setIcon(load_themed_icon("chevrons-right.svg", self.dark_mode))
        next_btn.setIconSize(QSize(16, 16))
        next_btn.setFixedSize(32, 32)
        next_btn.clicked.connect(self.find_next.emit)
        search_layout.addWidget(next_btn)
        layout.addLayout(search_layout)

        options_layout = QHBoxLayout()
        self.case_check = QCheckBox(tr("Case sensitive"))
        options_layout.addWidget(self.case_check)
        options_layout.addStretch()
        close_btn = QPushButton(tr("Close"))
        close_btn.clicked.connect(self.close)
        options_layout.addWidget(close_btn)
        layout.addLayout(options_layout)

    def _on_text_changed(self, text):
        self.find_requested.emit(text, self.case_check.isChecked(), True)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    def focus_search(self):
        self.search_input.setFocus()
        self.search_input.selectAll()


class SettingsDialog(BaseDialog):
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None, settings=None, dark_mode=False):
        super().__init__(parent, tr("Settings"), dark_mode)
        self.settings = settings or {}
        self.setFixedSize(620, 520)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        tabs = QTabWidget()

        tabs.addTab(self._create_general_tab(), tr("General"))
        tabs.addTab(self._create_appearance_tab(), tr("Appearance"))
        tabs.addTab(self._create_privacy_tab(), tr("Privacy"))
        tabs.addTab(self._create_security_tab(), tr("Security"))
        tabs.addTab(self._create_downloads_tab(), tr("Downloads"))
        layout.addWidget(tabs)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton(tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        save_btn = QPushButton(tr("Save"))
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _create_general_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        self.homepage_input = QLineEdit(self.settings.get('homepage', 'https://www.google.com'))
        layout.addRow(f"{tr('Homepage')}:", self.homepage_input)
        self.search_combo = QComboBox()
        self.search_combo.addItems(list(SEARCH_ENGINES.keys()))
        self.search_combo.setCurrentText(self.settings.get('search_engine', 'Google'))
        layout.addRow(f"{tr('Search Engine')}:", self.search_combo)
        self.language_combo = QComboBox()
        current_lang = self.settings.get('language', 'tr')
        for code, name in get_available_languages().items():
            self.language_combo.addItem(name, code)
        idx = self.language_combo.findData(current_lang)
        if idx >= 0:
            self.language_combo.setCurrentIndex(idx)
        layout.addRow(f"{tr('Language')}:", self.language_combo)
        self.startup_combo = QComboBox()
        self.startup_combo.addItems([tr("Open homepage"), tr("Continue last session"), tr("Open blank tab")])
        layout.addRow(f"{tr('Startup')}:", self.startup_combo)
        return widget

    def _create_appearance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        theme_group = QGroupBox(tr("Theme"))
        theme_layout = QVBoxLayout(theme_group)
        self.dark_mode_check = QCheckBox(tr("Dark Mode"))
        self.dark_mode_check.setChecked(self.settings.get('dark_mode', False))
        theme_layout.addWidget(self.dark_mode_check)
        layout.addWidget(theme_group)
        ui_group = QGroupBox(tr("Interface"))
        ui_layout = QVBoxLayout(ui_group)
        self.bookmarks_bar_check = QCheckBox(tr("Show bookmarks bar"))
        self.bookmarks_bar_check.setChecked(self.settings.get('show_bookmarks_bar', True))
        ui_layout.addWidget(self.bookmarks_bar_check)
        self.status_bar_check = QCheckBox(tr("Show status bar"))
        self.status_bar_check.setChecked(self.settings.get('show_status_bar', True))
        ui_layout.addWidget(self.status_bar_check)
        layout.addWidget(ui_group)
        layout.addStretch()
        return widget

    def _create_privacy_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        tracking_group = QGroupBox(tr("Tracking"))
        tracking_layout = QVBoxLayout(tracking_group)
        self.dnt_check = QCheckBox(tr("Send 'Do Not Track' request"))
        self.dnt_check.setChecked(self.settings.get('do_not_track', True))
        tracking_layout.addWidget(self.dnt_check)
        self.third_party_cookies_check = QCheckBox(tr("Block third-party cookies"))
        tracking_layout.addWidget(self.third_party_cookies_check)
        layout.addWidget(tracking_group)
        data_group = QGroupBox(tr("Data"))
        data_layout = QVBoxLayout(data_group)
        self.save_passwords_check = QCheckBox(tr("Save passwords"))
        self.save_passwords_check.setChecked(self.settings.get('save_passwords', True))
        data_layout.addWidget(self.save_passwords_check)
        self.autofill_check = QCheckBox(tr("Auto-fill forms"))
        self.autofill_check.setChecked(True)
        data_layout.addWidget(self.autofill_check)
        self.clear_on_exit_check = QCheckBox(tr("Clear data on exit"))
        data_layout.addWidget(self.clear_on_exit_check)
        clear_btn = QPushButton(tr("Clear Browsing Data..."))
        clear_btn.clicked.connect(self._show_clear_data_dialog)
        data_layout.addWidget(clear_btn)
        layout.addWidget(data_group)
        layout.addStretch()
        return widget

    def _create_security_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        security_group = QGroupBox(tr("Security"))
        security_layout = QVBoxLayout(security_group)
        self.ad_blocker_check = QCheckBox(tr("Ad blocker"))
        self.ad_blocker_check.setChecked(self.settings.get('ad_blocker', True))
        security_layout.addWidget(self.ad_blocker_check)
        self.phishing_check = QCheckBox(tr("Phishing protection"))
        self.phishing_check.setChecked(True)
        security_layout.addWidget(self.phishing_check)
        self.https_only_check = QCheckBox(tr("Use HTTPS only"))
        security_layout.addWidget(self.https_only_check)
        layout.addWidget(security_group)
        js_group = QGroupBox(tr("JavaScript"))
        js_layout = QVBoxLayout(js_group)
        self.js_enabled_check = QCheckBox(tr("Enable JavaScript"))
        self.js_enabled_check.setChecked(self.settings.get('javascript_enabled', True))
        js_layout.addWidget(self.js_enabled_check)
        layout.addWidget(js_group)
        layout.addStretch()
        return widget

    def _create_downloads_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        location_group = QGroupBox(tr("Location"))
        location_layout = QHBoxLayout(location_group)
        self.download_path_input = QLineEdit(self.settings.get('download_path', ''))
        location_layout.addWidget(self.download_path_input)
        browse_btn = QPushButton(tr("Browse..."))
        browse_btn.clicked.connect(self._browse_download_path)
        location_layout.addWidget(browse_btn)
        layout.addWidget(location_group)
        options_group = QGroupBox(tr("Options"))
        options_layout = QVBoxLayout(options_group)
        self.ask_download_check = QCheckBox(tr("Ask for location on each download"))
        options_layout.addWidget(self.ask_download_check)
        self.auto_open_check = QCheckBox(tr("Auto-open completed downloads"))
        options_layout.addWidget(self.auto_open_check)
        layout.addWidget(options_group)
        layout.addStretch()
        return widget

    def _browse_download_path(self):
        path = QFileDialog.getExistingDirectory(self, tr("Select Download Folder"))
        if path:
            self.download_path_input.setText(path)

    def _show_clear_data_dialog(self):
        dialog = ClearDataDialog(self, self.dark_mode)
        dialog.exec_()

    def _on_save(self):
        settings = {
            'homepage': self.homepage_input.text(),
            'search_engine': self.search_combo.currentText(),
            'language': self.language_combo.currentData(),
            'dark_mode': self.dark_mode_check.isChecked(),
            'show_bookmarks_bar': self.bookmarks_bar_check.isChecked(),
            'show_status_bar': self.status_bar_check.isChecked(),
            'do_not_track': self.dnt_check.isChecked(),
            'save_passwords': self.save_passwords_check.isChecked(),
            'clear_on_exit': self.clear_on_exit_check.isChecked(),
            'ad_blocker': self.ad_blocker_check.isChecked(),
            'javascript_enabled': self.js_enabled_check.isChecked(),
            'https_only': self.https_only_check.isChecked(),
            'download_path': self.download_path_input.text(),
            'ask_download': self.ask_download_check.isChecked(),
        }
        self.settings_changed.emit(settings)
        self.accept()


class ClearDataDialog(BaseDialog):
    clear_requested = pyqtSignal(dict)

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent, tr("Clear Browsing Data"), dark_mode)
        self.setFixedSize(420, 380)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel(f"{tr('Time range')}:"))
        self.time_combo = QComboBox()
        self.time_combo.addItems([tr("Last hour"), tr("Last 24 hours"), tr("Last 7 days"), tr("Last 4 weeks"), tr("All time")])
        time_layout.addWidget(self.time_combo)
        layout.addLayout(time_layout)

        data_group = QGroupBox(tr("Data to clear"))
        data_layout = QVBoxLayout(data_group)
        self.history_check = QCheckBox(tr("Browsing history"))
        self.history_check.setChecked(True)
        data_layout.addWidget(self.history_check)
        self.cookies_check = QCheckBox(tr("Cookies and site data"))
        self.cookies_check.setChecked(True)
        data_layout.addWidget(self.cookies_check)
        self.cache_check = QCheckBox(tr("Cache"))
        self.cache_check.setChecked(True)
        data_layout.addWidget(self.cache_check)
        self.downloads_check = QCheckBox(tr("Download history"))
        data_layout.addWidget(self.downloads_check)
        self.passwords_check = QCheckBox(tr("Saved passwords"))
        data_layout.addWidget(self.passwords_check)
        self.autofill_check = QCheckBox(tr("Autofill data"))
        data_layout.addWidget(self.autofill_check)
        layout.addWidget(data_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton(tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        clear_btn = QPushButton(tr("Clear Data"))
        clear_btn.setObjectName("dangerBtn")
        clear_btn.clicked.connect(self._on_clear)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)

    def _on_clear(self):
        data = {
            'time_range': self.time_combo.currentIndex(),
            'history': self.history_check.isChecked(),
            'cookies': self.cookies_check.isChecked(),
            'cache': self.cache_check.isChecked(),
            'downloads': self.downloads_check.isChecked(),
            'passwords': self.passwords_check.isChecked(),
            'autofill': self.autofill_check.isChecked(),
        }
        self.clear_requested.emit(data)
        self.accept()


class AboutDialog(BaseDialog):
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent, tr("About"), dark_mode)
        self.setFixedSize(460, 400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(32, 32, 32, 32)

        icon_label = QLabel()
        icon_label.setPixmap(load_themed_icon("globe.svg", self.dark_mode).pixmap(80, 80))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(96, 96)
        layout.addWidget(icon_label, 0, Qt.AlignCenter)

        name_label = QLabel(APP_NAME)
        name_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)

        version_label = QLabel(f"{tr('About')} {APP_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        desc_label = QLabel(tr("Modern, fast and secure web browser"))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        copyright_label = QLabel("© 2025 Alper Samur")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet(f"color: {theme['text_muted']};")
        layout.addWidget(copyright_label)

        layout.addStretch()
        close_btn = QPushButton(tr("Close"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
