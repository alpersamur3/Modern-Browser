"""
Dialog windows for Modern Browser
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QCheckBox,
                             QTabWidget, QWidget, QFormLayout, QSpinBox,
                             QGroupBox, QListWidget, QListWidgetItem,
                             QTextEdit, QFileDialog, QMessageBox, QFrame,
                             QScrollArea, QGridLayout, QSlider)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from ..utils.constants import (LIGHT_THEME, DARK_THEME, SEARCH_ENGINES, 
                               SUPPORTED_LANGUAGES, APP_NAME, APP_VERSION)


class BaseDialog(QDialog):
    """Base dialog with common styling"""
    
    def __init__(self, parent=None, title="", dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.setWindowTitle(title)
        self.setModal(True)
        self._apply_style()
    
    def _apply_style(self):
        theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['bg_primary']};
                color: {theme['text_primary']};
            }}
            QLabel {{
                color: {theme['text_primary']};
            }}
            QLineEdit, QTextEdit, QComboBox, QSpinBox {{
                background-color: {theme['bg_secondary']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px;
                color: {theme['text_primary']};
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {theme['accent']};
            }}
            QPushButton {{
                background-color: {theme['bg_tertiary']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px 16px;
                color: {theme['text_primary']};
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {theme['accent']};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: {theme['accent_hover']};
            }}
            QGroupBox {{
                border: 1px solid {theme['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
            QCheckBox {{
                color: {theme['text_primary']};
                spacing: 8px;
            }}
            QTabWidget::pane {{
                border: 1px solid {theme['border']};
                border-radius: 8px;
                background-color: {theme['bg_primary']};
            }}
            QTabBar::tab {{
                background-color: {theme['bg_secondary']};
                border: 1px solid {theme['border']};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {theme['bg_primary']};
                border-bottom: none;
            }}
        """)


class BookmarkDialog(BaseDialog):
    """Dialog for adding/editing bookmarks"""
    
    saved = pyqtSignal(str, str, str)  # title, url, folder
    
    def __init__(self, parent=None, title="", url="", folder="bookmarks_bar", dark_mode=False):
        super().__init__(parent, "Yer İmi Ekle", dark_mode)
        self.setFixedSize(400, 200)
        self._setup_ui(title, url, folder)
    
    def _setup_ui(self, title, url, folder):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Title input
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Başlık:"))
        self.title_input = QLineEdit(title)
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)
        
        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit(url)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Klasör:"))
        self.folder_combo = QComboBox()
        self.folder_combo.addItems(["Yer İmleri Çubuğu", "Diğer Yer İmleri"])
        folder_layout.addWidget(self.folder_combo)
        layout.addLayout(folder_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Kaydet")
        save_btn.clicked.connect(self._on_save)
        save_btn.setDefault(True)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _on_save(self):
        folder_map = {
            "Yer İmleri Çubuğu": "bookmarks_bar",
            "Diğer Yer İmleri": "other_bookmarks"
        }
        folder = folder_map.get(self.folder_combo.currentText(), "bookmarks_bar")
        self.saved.emit(self.title_input.text(), self.url_input.text(), folder)
        self.accept()


class FindDialog(BaseDialog):
    """Find in page dialog"""
    
    find_requested = pyqtSignal(str, bool, bool)  # text, case_sensitive, wrap
    find_next = pyqtSignal()
    find_prev = pyqtSignal()
    closed = pyqtSignal()
    
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent, "Sayfada Bul", dark_mode)
        self.setFixedSize(400, 120)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Search input
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ara...")
        self.search_input.textChanged.connect(self._on_text_changed)
        self.search_input.returnPressed.connect(self.find_next.emit)
        search_layout.addWidget(self.search_input)
        
        # Prev/Next buttons
        prev_btn = QPushButton("◀")
        prev_btn.setFixedWidth(40)
        prev_btn.clicked.connect(self.find_prev.emit)
        search_layout.addWidget(prev_btn)
        
        next_btn = QPushButton("▶")
        next_btn.setFixedWidth(40)
        next_btn.clicked.connect(self.find_next.emit)
        search_layout.addWidget(next_btn)
        
        layout.addLayout(search_layout)
        
        # Options
        options_layout = QHBoxLayout()
        self.case_check = QCheckBox("Büyük/küçük harf duyarlı")
        options_layout.addWidget(self.case_check)
        options_layout.addStretch()
        
        close_btn = QPushButton("Kapat")
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
    """Settings dialog with multiple tabs"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, settings=None, dark_mode=False):
        super().__init__(parent, "Ayarlar", dark_mode)
        self.settings = settings or {}
        self.setFixedSize(600, 500)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # General tab
        general_tab = self._create_general_tab()
        tabs.addTab(general_tab, "Genel")
        
        # Appearance tab
        appearance_tab = self._create_appearance_tab()
        tabs.addTab(appearance_tab, "Görünüm")
        
        # Privacy tab
        privacy_tab = self._create_privacy_tab()
        tabs.addTab(privacy_tab, "Gizlilik")
        
        # Security tab
        security_tab = self._create_security_tab()
        tabs.addTab(security_tab, "Güvenlik")
        
        # Downloads tab
        downloads_tab = self._create_downloads_tab()
        tabs.addTab(downloads_tab, "İndirmeler")
        
        layout.addWidget(tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Kaydet")
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_general_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(16)
        
        # Homepage
        self.homepage_input = QLineEdit(self.settings.get('homepage', 'https://www.google.com'))
        layout.addRow("Ana Sayfa:", self.homepage_input)
        
        # Search engine
        self.search_combo = QComboBox()
        self.search_combo.addItems(list(SEARCH_ENGINES.keys()))
        current_engine = self.settings.get('search_engine', 'Google')
        self.search_combo.setCurrentText(current_engine)
        layout.addRow("Arama Motoru:", self.search_combo)
        
        # Language
        self.language_combo = QComboBox()
        for code, name in SUPPORTED_LANGUAGES.items():
            self.language_combo.addItem(name, code)
        layout.addRow("Dil:", self.language_combo)
        
        # Startup behavior
        self.startup_combo = QComboBox()
        self.startup_combo.addItems(["Ana sayfayı aç", "Son oturumu sürdür", "Boş sekme aç"])
        layout.addRow("Başlangıç:", self.startup_combo)
        
        return widget
    
    def _create_appearance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme group
        theme_group = QGroupBox("Tema")
        theme_layout = QVBoxLayout(theme_group)
        
        self.dark_mode_check = QCheckBox("Karanlık mod")
        self.dark_mode_check.setChecked(self.settings.get('dark_mode', False))
        theme_layout.addWidget(self.dark_mode_check)
        
        layout.addWidget(theme_group)
        
        # UI group
        ui_group = QGroupBox("Arayüz")
        ui_layout = QVBoxLayout(ui_group)
        
        self.bookmarks_bar_check = QCheckBox("Yer imleri çubuğunu göster")
        self.bookmarks_bar_check.setChecked(self.settings.get('show_bookmarks_bar', True))
        ui_layout.addWidget(self.bookmarks_bar_check)
        
        self.status_bar_check = QCheckBox("Durum çubuğunu göster")
        self.status_bar_check.setChecked(self.settings.get('show_status_bar', True))
        ui_layout.addWidget(self.status_bar_check)
        
        layout.addWidget(ui_group)
        layout.addStretch()
        
        return widget
    
    def _create_privacy_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tracking group
        tracking_group = QGroupBox("İzleme")
        tracking_layout = QVBoxLayout(tracking_group)
        
        self.dnt_check = QCheckBox("'İzlenme' isteği gönder")
        self.dnt_check.setChecked(self.settings.get('do_not_track', True))
        tracking_layout.addWidget(self.dnt_check)
        
        self.third_party_cookies_check = QCheckBox("Üçüncü taraf çerezleri engelle")
        tracking_layout.addWidget(self.third_party_cookies_check)
        
        layout.addWidget(tracking_group)
        
        # Data group
        data_group = QGroupBox("Veri")
        data_layout = QVBoxLayout(data_group)
        
        self.save_passwords_check = QCheckBox("Parolaları kaydet")
        self.save_passwords_check.setChecked(self.settings.get('save_passwords', True))
        data_layout.addWidget(self.save_passwords_check)
        
        self.autofill_check = QCheckBox("Formları otomatik doldur")
        self.autofill_check.setChecked(True)
        data_layout.addWidget(self.autofill_check)
        
        self.clear_on_exit_check = QCheckBox("Çıkışta verileri temizle")
        data_layout.addWidget(self.clear_on_exit_check)
        
        # Clear data button
        clear_btn = QPushButton("Tarama Verilerini Temizle...")
        clear_btn.clicked.connect(self._show_clear_data_dialog)
        data_layout.addWidget(clear_btn)
        
        layout.addWidget(data_group)
        layout.addStretch()
        
        return widget
    
    def _create_security_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Security group
        security_group = QGroupBox("Güvenlik")
        security_layout = QVBoxLayout(security_group)
        
        self.ad_blocker_check = QCheckBox("Reklam engelleyici")
        self.ad_blocker_check.setChecked(self.settings.get('ad_blocker', True))
        security_layout.addWidget(self.ad_blocker_check)
        
        self.phishing_check = QCheckBox("Kimlik avı koruması")
        self.phishing_check.setChecked(True)
        security_layout.addWidget(self.phishing_check)
        
        self.https_only_check = QCheckBox("Yalnızca HTTPS kullan")
        security_layout.addWidget(self.https_only_check)
        
        layout.addWidget(security_group)
        
        # JavaScript group
        js_group = QGroupBox("JavaScript")
        js_layout = QVBoxLayout(js_group)
        
        self.js_enabled_check = QCheckBox("JavaScript'i etkinleştir")
        self.js_enabled_check.setChecked(self.settings.get('javascript_enabled', True))
        js_layout.addWidget(self.js_enabled_check)
        
        layout.addWidget(js_group)
        layout.addStretch()
        
        return widget
    
    def _create_downloads_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Location group
        location_group = QGroupBox("Konum")
        location_layout = QHBoxLayout(location_group)
        
        self.download_path_input = QLineEdit(self.settings.get('download_path', ''))
        location_layout.addWidget(self.download_path_input)
        
        browse_btn = QPushButton("Gözat...")
        browse_btn.clicked.connect(self._browse_download_path)
        location_layout.addWidget(browse_btn)
        
        layout.addWidget(location_group)
        
        # Options group
        options_group = QGroupBox("Seçenekler")
        options_layout = QVBoxLayout(options_group)
        
        self.ask_download_check = QCheckBox("Her indirmede konum sor")
        options_layout.addWidget(self.ask_download_check)
        
        self.auto_open_check = QCheckBox("Tamamlanan indirmeleri otomatik aç")
        options_layout.addWidget(self.auto_open_check)
        
        layout.addWidget(options_group)
        layout.addStretch()
        
        return widget
    
    def _browse_download_path(self):
        path = QFileDialog.getExistingDirectory(self, "İndirme Klasörü Seç")
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
            'ask_download': self.ask_download_check.isChecked()
        }
        self.settings_changed.emit(settings)
        self.accept()


class ClearDataDialog(BaseDialog):
    """Dialog for clearing browsing data"""
    
    clear_requested = pyqtSignal(dict)
    
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent, "Tarama Verilerini Temizle", dark_mode)
        self.setFixedSize(400, 350)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Time range
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Zaman aralığı:"))
        self.time_combo = QComboBox()
        self.time_combo.addItems(["Son 1 saat", "Son 24 saat", "Son 7 gün", "Son 4 hafta", "Tüm zamanlar"])
        time_layout.addWidget(self.time_combo)
        layout.addLayout(time_layout)
        
        # Data types
        data_group = QGroupBox("Temizlenecek veriler")
        data_layout = QVBoxLayout(data_group)
        
        self.history_check = QCheckBox("Tarama geçmişi")
        self.history_check.setChecked(True)
        data_layout.addWidget(self.history_check)
        
        self.cookies_check = QCheckBox("Çerezler ve site verileri")
        self.cookies_check.setChecked(True)
        data_layout.addWidget(self.cookies_check)
        
        self.cache_check = QCheckBox("Önbellek")
        self.cache_check.setChecked(True)
        data_layout.addWidget(self.cache_check)
        
        self.downloads_check = QCheckBox("İndirme geçmişi")
        data_layout.addWidget(self.downloads_check)
        
        self.passwords_check = QCheckBox("Kaydedilmiş parolalar")
        data_layout.addWidget(self.passwords_check)
        
        self.autofill_check = QCheckBox("Otomatik doldurma verileri")
        data_layout.addWidget(self.autofill_check)
        
        layout.addWidget(data_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        clear_btn = QPushButton("Verileri Temizle")
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
            'autofill': self.autofill_check.isChecked()
        }
        self.clear_requested.emit(data)
        self.accept()


class AboutDialog(BaseDialog):
    """About dialog"""
    
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent, "Hakkında", dark_mode)
        self.setFixedSize(400, 300)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        
        # Logo/Icon
        icon_label = QLabel("🌐")
        icon_label.setFont(QFont("Segoe UI", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # App name
        name_label = QLabel(APP_NAME)
        name_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # Version
        version_label = QLabel(f"Sürüm {APP_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        desc_label = QLabel("Modern, hızlı ve güvenli bir web tarayıcısı")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Copyright
        copyright_label = QLabel("© 2025 Alper Samur")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: #666;")
        layout.addWidget(copyright_label)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
