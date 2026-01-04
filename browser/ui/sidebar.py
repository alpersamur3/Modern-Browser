"""
Modern Sidebar for Browser
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QLineEdit,
                             QListWidget, QListWidgetItem, QStackedWidget,
                             QTreeWidget, QTreeWidgetItem, QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont
from ..utils.constants import LIGHT_THEME, DARK_THEME, TRANSLATIONS


class SidebarButton(QPushButton):
    """Custom sidebar navigation button"""
    
    def __init__(self, icon, text, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setIcon(QIcon.fromTheme(icon) if icon else QIcon())
        self.setCheckable(True)
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)


class BookmarkItem(QFrame):
    """Widget for displaying a bookmark item"""
    
    clicked = pyqtSignal(str)  # url
    delete_clicked = pyqtSignal(str)  # bookmark_id
    
    def __init__(self, bookmark, parent=None):
        super().__init__(parent)
        self.bookmark = bookmark
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Favicon placeholder
        icon_label = QLabel("🔖")
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(self.bookmark.title[:30])
        title_label.setToolTip(self.bookmark.url)
        layout.addWidget(title_label, 1)
        
        # Delete button
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(20, 20)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.bookmark.id))
        layout.addWidget(delete_btn)
        
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.bookmark.url)


class HistoryItem(QFrame):
    """Widget for displaying a history item"""
    
    clicked = pyqtSignal(str)  # url
    
    def __init__(self, entry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)
        
        # Title
        title_label = QLabel(self.entry.title[:40])
        title_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(title_label)
        
        # URL (smaller)
        url_label = QLabel(self.entry.url[:50])
        url_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(url_label)
        
        self.setCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.entry.url)


class DownloadItem(QFrame):
    """Widget for displaying a download item"""
    
    open_clicked = pyqtSignal(str)  # download_id
    cancel_clicked = pyqtSignal(str)  # download_id
    
    def __init__(self, download, parent=None):
        super().__init__(parent)
        self.download = download
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Filename
        name_label = QLabel(self.download.filename[:30])
        name_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(name_label)
        
        # Progress/status
        status_label = QLabel(f"{self.download.progress}% - {self.download.size_text}")
        status_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        if self.download.status == 'completed':
            open_btn = QPushButton("Aç")
            open_btn.clicked.connect(lambda: self.open_clicked.emit(self.download.id))
            btn_layout.addWidget(open_btn)
        elif self.download.status == 'downloading':
            cancel_btn = QPushButton("İptal")
            cancel_btn.clicked.connect(lambda: self.cancel_clicked.emit(self.download.id))
            btn_layout.addWidget(cancel_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)


class Sidebar(QWidget):
    """Modern sidebar with bookmarks, history, and downloads"""
    
    # Signals
    bookmark_clicked = pyqtSignal(str)
    history_clicked = pyqtSignal(str)
    download_open_clicked = pyqtSignal(str)
    download_cancel_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.language = "tr"
        self._current_panel = None
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Setup sidebar UI"""
        self.setFixedWidth(300)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(8, 8, 8, 8)
        nav_layout.setSpacing(4)
        
        self.bookmarks_btn = SidebarButton("bookmark", "🔖")
        self.bookmarks_btn.setToolTip("Yer İmleri")
        self.bookmarks_btn.clicked.connect(lambda: self.show_panel("bookmarks"))
        
        self.history_btn = SidebarButton("history", "📜")
        self.history_btn.setToolTip("Geçmiş")
        self.history_btn.clicked.connect(lambda: self.show_panel("history"))
        
        self.downloads_btn = SidebarButton("download", "⬇️")
        self.downloads_btn.setToolTip("İndirmeler")
        self.downloads_btn.clicked.connect(lambda: self.show_panel("downloads"))
        
        for btn in [self.bookmarks_btn, self.history_btn, self.downloads_btn]:
            btn.setFixedSize(40, 40)
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.hide)
        nav_layout.addWidget(close_btn)
        
        main_layout.addLayout(nav_layout)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ara...")
        self.search_input.textChanged.connect(self._on_search)
        main_layout.addWidget(self.search_input)
        
        # Stacked widget for panels
        self.stack = QStackedWidget()
        
        # Bookmarks panel
        self.bookmarks_panel = self._create_bookmarks_panel()
        self.stack.addWidget(self.bookmarks_panel)
        
        # History panel
        self.history_panel = self._create_history_panel()
        self.stack.addWidget(self.history_panel)
        
        # Downloads panel
        self.downloads_panel = self._create_downloads_panel()
        self.stack.addWidget(self.downloads_panel)
        
        main_layout.addWidget(self.stack)
        
        # Show bookmarks by default
        self.show_panel("bookmarks")
    
    def _create_bookmarks_panel(self):
        """Create bookmarks panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel("Yer İmleri")
        header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header.setContentsMargins(12, 8, 12, 8)
        layout.addWidget(header)
        
        # Scroll area for bookmarks
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.bookmarks_container = QWidget()
        self.bookmarks_layout = QVBoxLayout(self.bookmarks_container)
        self.bookmarks_layout.setAlignment(Qt.AlignTop)
        self.bookmarks_layout.setContentsMargins(8, 0, 8, 8)
        self.bookmarks_layout.setSpacing(4)
        
        scroll.setWidget(self.bookmarks_container)
        layout.addWidget(scroll)
        
        return panel
    
    def _create_history_panel(self):
        """Create history panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with clear button
        header_layout = QHBoxLayout()
        header = QLabel("Geçmiş")
        header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        clear_btn = QPushButton("Temizle")
        clear_btn.setFixedHeight(24)
        self.clear_history_btn = clear_btn
        header_layout.addWidget(clear_btn)
        
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setContentsMargins(12, 8, 12, 8)
        layout.addWidget(header_widget)
        
        # Scroll area for history
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setAlignment(Qt.AlignTop)
        self.history_layout.setContentsMargins(8, 0, 8, 8)
        self.history_layout.setSpacing(4)
        
        scroll.setWidget(self.history_container)
        layout.addWidget(scroll)
        
        return panel
    
    def _create_downloads_panel(self):
        """Create downloads panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel("İndirmeler")
        header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header.setContentsMargins(12, 8, 12, 8)
        layout.addWidget(header)
        
        # Scroll area for downloads
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.downloads_container = QWidget()
        self.downloads_layout = QVBoxLayout(self.downloads_container)
        self.downloads_layout.setAlignment(Qt.AlignTop)
        self.downloads_layout.setContentsMargins(8, 0, 8, 8)
        self.downloads_layout.setSpacing(4)
        
        scroll.setWidget(self.downloads_container)
        layout.addWidget(scroll)
        
        return panel
    
    def _apply_style(self):
        """Apply styling"""
        theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
            }}
            
            QLineEdit {{
                background-color: {theme['bg_tertiary']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px 12px;
                margin: 8px;
                font-size: 13px;
            }}
            
            QLineEdit:focus {{
                border-color: {theme['accent']};
            }}
            
            QPushButton {{
                background-color: {theme['bg_tertiary']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }}
            
            QPushButton:hover {{
                background-color: {theme['accent']};
                color: white;
            }}
            
            QPushButton:checked {{
                background-color: {theme['accent']};
                color: white;
            }}
            
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            
            QFrame {{
                background-color: {theme['bg_primary']};
                border-radius: 6px;
                margin: 2px 0;
            }}
            
            QFrame:hover {{
                background-color: {theme['bg_tertiary']};
            }}
        """)
    
    def set_dark_mode(self, dark_mode):
        """Toggle dark mode"""
        self.dark_mode = dark_mode
        self._apply_style()
    
    def show_panel(self, panel_name):
        """Show a specific panel"""
        self._current_panel = panel_name
        
        # Update button states
        self.bookmarks_btn.setChecked(panel_name == "bookmarks")
        self.history_btn.setChecked(panel_name == "history")
        self.downloads_btn.setChecked(panel_name == "downloads")
        
        # Show appropriate panel
        if panel_name == "bookmarks":
            self.stack.setCurrentWidget(self.bookmarks_panel)
        elif panel_name == "history":
            self.stack.setCurrentWidget(self.history_panel)
        elif panel_name == "downloads":
            self.stack.setCurrentWidget(self.downloads_panel)
        
        self.show()
    
    def _on_search(self, text):
        """Handle search input"""
        # Emit appropriate search signal based on current panel
        pass
    
    def update_bookmarks(self, bookmarks):
        """Update bookmarks list"""
        # Clear existing
        while self.bookmarks_layout.count():
            item = self.bookmarks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new
        for bookmark in bookmarks:
            item = BookmarkItem(bookmark)
            item.clicked.connect(self.bookmark_clicked.emit)
            self.bookmarks_layout.addWidget(item)
        
        if not bookmarks:
            empty_label = QLabel("Henüz yer imi yok")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #666; padding: 20px;")
            self.bookmarks_layout.addWidget(empty_label)
    
    def update_history(self, entries):
        """Update history list"""
        # Clear existing
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new
        for entry in entries[:50]:  # Limit to 50 items
            item = HistoryItem(entry)
            item.clicked.connect(self.history_clicked.emit)
            self.history_layout.addWidget(item)
        
        if not entries:
            empty_label = QLabel("Henüz geçmiş yok")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #666; padding: 20px;")
            self.history_layout.addWidget(empty_label)
    
    def update_downloads(self, downloads):
        """Update downloads list"""
        # Clear existing
        while self.downloads_layout.count():
            item = self.downloads_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new
        for download in downloads:
            item = DownloadItem(download)
            item.open_clicked.connect(self.download_open_clicked.emit)
            item.cancel_clicked.connect(self.download_cancel_clicked.emit)
            self.downloads_layout.addWidget(item)
        
        if not downloads:
            empty_label = QLabel("Henüz indirme yok")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #666; padding: 20px;")
            self.downloads_layout.addWidget(empty_label)
