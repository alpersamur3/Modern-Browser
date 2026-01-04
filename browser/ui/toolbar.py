"""
Modern Toolbar for Browser
"""

from PyQt5.QtWidgets import (QToolBar, QWidget, QHBoxLayout, QLineEdit, 
                             QPushButton, QMenu, QAction, QLabel, QCompleter,
                             QToolButton, QSizePolicy, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QStringListModel, QUrl
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from ..utils.constants import LIGHT_THEME, DARK_THEME, SHORTCUTS


class AddressBar(QLineEdit):
    """Modern address bar with search suggestions"""
    
    return_pressed = pyqtSignal(str)
    focus_changed = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Ara veya URL gir...")
        self._setup_completer()
    
    def _setup_completer(self):
        """Setup autocomplete"""
        self.completer_model = QStringListModel()
        completer = QCompleter(self.completer_model)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.setCompleter(completer)
    
    def update_suggestions(self, suggestions):
        """Update autocomplete suggestions"""
        self.completer_model.setStringList(suggestions)
    
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.selectAll()
        self.focus_changed.emit(True)
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.focus_changed.emit(False)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.return_pressed.emit(self.text())
        else:
            super().keyPressEvent(event)


class NavigationButton(QToolButton):
    """Styled navigation button"""
    
    def __init__(self, icon_text, tooltip="", parent=None):
        super().__init__(parent)
        self.setText(icon_text)
        self.setToolTip(tooltip)
        self.setFixedSize(36, 36)
        self.setCursor(Qt.PointingHandCursor)


class BrowserToolbar(QToolBar):
    """Modern browser toolbar with navigation, address bar, and actions"""
    
    # Signals
    back_clicked = pyqtSignal()
    forward_clicked = pyqtSignal()
    reload_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    home_clicked = pyqtSignal()
    navigate_requested = pyqtSignal(str)
    new_tab_clicked = pyqtSignal()
    private_tab_clicked = pyqtSignal()
    bookmark_clicked = pyqtSignal()
    menu_clicked = pyqtSignal()
    downloads_clicked = pyqtSignal()
    history_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self._is_loading = False
        self._is_bookmarked = False
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Setup toolbar UI"""
        self.setMovable(False)
        self.setFloatable(False)
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        self.setFixedHeight(52)
        
        # Main container
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Navigation buttons
        self.back_btn = NavigationButton("◀", "Geri (Alt+Left)")
        self.back_btn.clicked.connect(self.back_clicked.emit)
        layout.addWidget(self.back_btn)
        
        self.forward_btn = NavigationButton("▶", "İleri (Alt+Right)")
        self.forward_btn.clicked.connect(self.forward_clicked.emit)
        layout.addWidget(self.forward_btn)
        
        self.reload_btn = NavigationButton("↻", "Yenile (F5)")
        self.reload_btn.clicked.connect(self._on_reload_click)
        layout.addWidget(self.reload_btn)
        
        self.home_btn = NavigationButton("🏠", "Ana Sayfa")
        self.home_btn.clicked.connect(self.home_clicked.emit)
        layout.addWidget(self.home_btn)
        
        layout.addSpacing(8)
        
        # Security indicator
        self.security_indicator = QLabel("🔒")
        self.security_indicator.setFixedSize(24, 24)
        self.security_indicator.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.security_indicator)
        
        # Address bar
        self.address_bar = AddressBar()
        self.address_bar.return_pressed.connect(self.navigate_requested.emit)
        self.address_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.address_bar.setFixedHeight(36)
        layout.addWidget(self.address_bar)
        
        # Bookmark button
        self.bookmark_btn = NavigationButton("☆", "Yer İmine Ekle (Ctrl+D)")
        self.bookmark_btn.clicked.connect(self.bookmark_clicked.emit)
        layout.addWidget(self.bookmark_btn)
        
        layout.addSpacing(8)
        
        # Action buttons
        self.downloads_btn = NavigationButton("⬇️", "İndirmeler (Ctrl+J)")
        self.downloads_btn.clicked.connect(self.downloads_clicked.emit)
        layout.addWidget(self.downloads_btn)
        
        self.new_tab_btn = NavigationButton("+", "Yeni Sekme (Ctrl+T)")
        self.new_tab_btn.clicked.connect(self.new_tab_clicked.emit)
        layout.addWidget(self.new_tab_btn)
        
        self.private_btn = NavigationButton("🕶️", "Gizli Sekme (Ctrl+Shift+N)")
        self.private_btn.clicked.connect(self.private_tab_clicked.emit)
        layout.addWidget(self.private_btn)
        
        # Menu button
        self.menu_btn = NavigationButton("☰", "Menü")
        self.menu_btn.clicked.connect(self.menu_clicked.emit)
        layout.addWidget(self.menu_btn)
        
        self.addWidget(container)
    
    def _apply_style(self):
        """Apply styling"""
        theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        
        self.setStyleSheet(f"""
            QToolBar {{
                background-color: {theme['bg_primary']};
                border: none;
                border-bottom: 1px solid {theme['border']};
                spacing: 4px;
            }}
            
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                color: {theme['text_primary']};
            }}
            
            QToolButton:hover {{
                background-color: {theme['bg_tertiary']};
            }}
            
            QToolButton:pressed {{
                background-color: {theme['bg_secondary']};
            }}
            
            QToolButton:disabled {{
                color: {theme['text_secondary']};
                opacity: 0.5;
            }}
            
            QLineEdit {{
                background-color: {theme['bg_secondary']};
                border: 2px solid {theme['border']};
                border-radius: 18px;
                padding: 0 16px;
                font-size: 14px;
                color: {theme['text_primary']};
                selection-background-color: {theme['accent']};
            }}
            
            QLineEdit:focus {{
                border-color: {theme['accent']};
                background-color: {theme['bg_primary']};
            }}
            
            QLabel {{
                color: {theme['text_primary']};
            }}
        """)
    
    def set_dark_mode(self, dark_mode):
        """Toggle dark mode"""
        self.dark_mode = dark_mode
        self._apply_style()
    
    def _on_reload_click(self):
        """Handle reload/stop button click"""
        if self._is_loading:
            self.stop_clicked.emit()
        else:
            self.reload_clicked.emit()
    
    def set_loading(self, loading):
        """Set loading state"""
        self._is_loading = loading
        if loading:
            self.reload_btn.setText("✕")
            self.reload_btn.setToolTip("Durdur (Esc)")
        else:
            self.reload_btn.setText("↻")
            self.reload_btn.setToolTip("Yenile (F5)")
    
    def set_url(self, url):
        """Set address bar URL"""
        if isinstance(url, QUrl):
            url = url.toString()
        self.address_bar.setText(url)
        self.address_bar.setCursorPosition(0)
    
    def get_url(self):
        """Get address bar text"""
        return self.address_bar.text()
    
    def focus_address_bar(self):
        """Focus and select address bar"""
        self.address_bar.setFocus()
        self.address_bar.selectAll()
    
    def set_security(self, is_secure):
        """Set security indicator"""
        if is_secure:
            self.security_indicator.setText("🔒")
            self.security_indicator.setToolTip("Güvenli bağlantı (HTTPS)")
            self.security_indicator.setStyleSheet("color: #34a853;")
        else:
            self.security_indicator.setText("⚠️")
            self.security_indicator.setToolTip("Güvensiz bağlantı")
            self.security_indicator.setStyleSheet("color: #ea4335;")
    
    def set_bookmarked(self, is_bookmarked):
        """Set bookmark button state"""
        self._is_bookmarked = is_bookmarked
        if is_bookmarked:
            self.bookmark_btn.setText("★")
            self.bookmark_btn.setToolTip("Yer İminden Kaldır")
        else:
            self.bookmark_btn.setText("☆")
            self.bookmark_btn.setToolTip("Yer İmine Ekle (Ctrl+D)")
    
    def set_navigation_state(self, can_back, can_forward):
        """Set navigation button states"""
        self.back_btn.setEnabled(can_back)
        self.forward_btn.setEnabled(can_forward)
    
    def update_suggestions(self, suggestions):
        """Update address bar suggestions"""
        self.address_bar.update_suggestions(suggestions)
