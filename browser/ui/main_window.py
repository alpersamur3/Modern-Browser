"""
Main Window for Modern Browser
"""

import os
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QTabBar, QWidget, 
                             QVBoxLayout, QHBoxLayout, QShortcut, QMenu,
                             QAction, QMessageBox, QFileDialog, QApplication,
                             QSplitter, QPushButton, QLabel)
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QTimer, QSize, QStandardPaths
from PyQt5.QtGui import QKeySequence, QIcon, QColor, QFont
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

from ..core.browser_tab import BrowserTab
from ..core.browser_engine import BrowserEngine
from ..core.settings_manager import SettingsManager
from ..features.bookmarks import BookmarkManager
from ..features.history import HistoryManager
from ..features.downloads import DownloadManager
from ..features.ad_blocker import AdBlocker, ElementHider
from ..features.password_manager import PasswordManager
from ..features.search import SearchManager
from ..features.reader_mode import ReaderMode
from .toolbar import BrowserToolbar
from .sidebar import Sidebar
from .status_bar import StatusBar
from .dialogs import (BookmarkDialog, FindDialog, SettingsDialog, 
                      AboutDialog, ClearDataDialog)
from ..utils.constants import (LIGHT_THEME, DARK_THEME, APP_NAME, APP_VERSION,
                               SHORTCUTS, DEFAULT_HOME_URL)
from ..utils.helpers import extract_domain, truncate_text


class ModernTabBar(QTabBar):
    """Custom tab bar with modern styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setExpanding(False)
        self.setElideMode(Qt.ElideRight)
        self.setDocumentMode(True)
    
    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        size.setWidth(min(200, max(100, size.width())))
        size.setHeight(36)
        return size


class ModernTabWidget(QTabWidget):
    """Custom tab widget with modern features"""
    
    new_tab_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Use custom tab bar
        self._tab_bar = ModernTabBar()
        self.setTabBar(self._tab_bar)
        
        # Add new tab button
        self._add_btn = QPushButton("+")
        self._add_btn.setFixedSize(28, 28)
        self._add_btn.clicked.connect(self.new_tab_requested.emit)
        self._add_btn.setCursor(Qt.PointingHandCursor)
        self.setCornerWidget(self._add_btn, Qt.TopRightCorner)
    
    def contextMenuEvent(self, event):
        """Show tab context menu"""
        index = self.tabBar().tabAt(event.pos())
        if index >= 0:
            menu = QMenu(self)
            
            reload_action = menu.addAction("Yenile")
            reload_action.triggered.connect(lambda: self.widget(index).reload())
            
            duplicate_action = menu.addAction("Sekmeyi Kopyala")
            duplicate_action.setData(("duplicate", index))
            
            menu.addSeparator()
            
            pin_action = menu.addAction("Sekmeyi Sabitle")
            mute_action = menu.addAction("Sekmeyi Sessize Al")
            
            menu.addSeparator()
            
            close_action = menu.addAction("Sekmeyi Kapat")
            close_action.triggered.connect(lambda: self.tabCloseRequested.emit(index))
            
            close_others_action = menu.addAction("Diğerlerini Kapat")
            close_right_action = menu.addAction("Sağdakileri Kapat")
            
            menu.exec_(event.globalPos())


class MainWindow(QMainWindow):
    """Main browser window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.settings_manager = SettingsManager()
        self.engine = BrowserEngine()
        self.bookmark_manager = BookmarkManager()
        self.history_manager = HistoryManager()
        self.download_manager = DownloadManager()
        self.search_manager = SearchManager()
        self.reader_mode = ReaderMode()
        
        # State
        self._dark_mode = self.settings_manager.dark_mode
        self._closed_tabs = []  # For reopening closed tabs
        self._find_dialog = None
        
        # Setup UI
        self._setup_window()
        self._setup_ad_blocker()
        self._setup_ui()
        self._setup_menu()
        self._setup_shortcuts()
        self._connect_signals()
        self._apply_style()
        
        # Load initial tab
        self.add_new_tab(QUrl(self.settings_manager.homepage))
    
    def _setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 800)
        self.setMinimumSize(800, 600)
        
        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _setup_ad_blocker(self):
        """Setup ad blocker"""
        if self.settings_manager.ad_blocker_enabled:
            self.ad_blocker = AdBlocker()
            self.engine.default_profile.setUrlRequestInterceptor(self.ad_blocker)
        else:
            self.ad_blocker = None
    
    def _setup_ui(self):
        """Setup main UI"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar(dark_mode=self._dark_mode)
        self.sidebar.hide()
        self.sidebar.bookmark_clicked.connect(lambda url: self.add_new_tab(QUrl(url)))
        self.sidebar.history_clicked.connect(lambda url: self.add_new_tab(QUrl(url)))
        self.sidebar.download_open_clicked.connect(self.download_manager.open_file)
        self.sidebar.download_cancel_clicked.connect(self.download_manager.cancel_download)
        self.sidebar.clear_history_btn.clicked.connect(self._clear_history)
        main_layout.addWidget(self.sidebar)
        
        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = BrowserToolbar(dark_mode=self._dark_mode)
        content_layout.addWidget(self.toolbar)
        
        # Tab widget
        self.tabs = ModernTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.tabs.new_tab_requested.connect(lambda: self.add_new_tab())
        content_layout.addWidget(self.tabs)
        
        main_layout.addWidget(content_widget)
        
        # Status bar
        self.status_bar = StatusBar(dark_mode=self._dark_mode)
        self.setStatusBar(self.status_bar)
        self.status_bar.zoom_clicked.connect(self._reset_zoom)
        self.status_bar.ad_blocker_clicked.connect(self._toggle_ad_blocker)
    
    def _setup_menu(self):
        """Setup main menu"""
        self.main_menu = QMenu(self)
        
        # File section
        new_tab = self.main_menu.addAction("Yeni Sekme")
        new_tab.setShortcut(SHORTCUTS['new_tab'])
        new_tab.triggered.connect(lambda: self.add_new_tab())
        
        new_private = self.main_menu.addAction("Yeni Gizli Sekme")
        new_private.setShortcut(SHORTCUTS['private_tab'])
        new_private.triggered.connect(lambda: self.add_new_tab(private=True))
        
        reopen_tab = self.main_menu.addAction("Kapatılan Sekmeyi Aç")
        reopen_tab.setShortcut(SHORTCUTS['reopen_tab'])
        reopen_tab.triggered.connect(self._reopen_closed_tab)
        
        self.main_menu.addSeparator()
        
        # Navigation
        self.main_menu.addAction("Geçmiş", self._show_history).setShortcut(SHORTCUTS['history_panel'])
        self.main_menu.addAction("Yer İmleri", self._show_bookmarks).setShortcut(SHORTCUTS['bookmarks_panel'])
        self.main_menu.addAction("İndirmeler", self._show_downloads).setShortcut(SHORTCUTS['downloads_panel'])
        
        self.main_menu.addSeparator()
        
        # View
        view_menu = self.main_menu.addMenu("Görünüm")
        
        zoom_in = view_menu.addAction("Yakınlaştır")
        zoom_in.setShortcut(SHORTCUTS['zoom_in'])
        zoom_in.triggered.connect(self._zoom_in)
        
        zoom_out = view_menu.addAction("Uzaklaştır")
        zoom_out.setShortcut(SHORTCUTS['zoom_out'])
        zoom_out.triggered.connect(self._zoom_out)
        
        zoom_reset = view_menu.addAction("Yakınlaştırmayı Sıfırla")
        zoom_reset.setShortcut(SHORTCUTS['zoom_reset'])
        zoom_reset.triggered.connect(self._reset_zoom)
        
        view_menu.addSeparator()
        
        fullscreen = view_menu.addAction("Tam Ekran")
        fullscreen.setShortcut(SHORTCUTS['fullscreen'])
        fullscreen.triggered.connect(self._toggle_fullscreen)
        
        # Tools
        tools_menu = self.main_menu.addMenu("Araçlar")
        
        find = tools_menu.addAction("Sayfada Bul")
        find.setShortcut(SHORTCUTS['find'])
        find.triggered.connect(self._show_find_dialog)
        
        tools_menu.addSeparator()
        
        reader = tools_menu.addAction("Okuma Modu")
        reader.setShortcut(SHORTCUTS['reader_mode'])
        reader.triggered.connect(self._toggle_reader_mode)
        
        screenshot = tools_menu.addAction("Ekran Görüntüsü")
        screenshot.setShortcut(SHORTCUTS['screenshot'])
        screenshot.triggered.connect(self._take_screenshot)
        
        tools_menu.addSeparator()
        
        view_source = tools_menu.addAction("Kaynağı Görüntüle")
        view_source.setShortcut(SHORTCUTS['view_source'])
        view_source.triggered.connect(self._view_source)
        
        dev_tools = tools_menu.addAction("Geliştirici Araçları")
        dev_tools.setShortcut(SHORTCUTS['dev_tools'])
        dev_tools.triggered.connect(self._open_dev_tools)
        
        tools_menu.addSeparator()
        
        print_page = tools_menu.addAction("Yazdır")
        print_page.setShortcut(SHORTCUTS['print'])
        print_page.triggered.connect(self._print_page)
        
        self.main_menu.addSeparator()
        
        # Settings
        dark_mode = self.main_menu.addAction("Karanlık Mod")
        dark_mode.setCheckable(True)
        dark_mode.setChecked(self._dark_mode)
        dark_mode.triggered.connect(self._toggle_dark_mode)
        
        settings = self.main_menu.addAction("Ayarlar")
        settings.setShortcut(SHORTCUTS['settings'])
        settings.triggered.connect(self._show_settings)
        
        self.main_menu.addSeparator()
        
        # About & Quit
        about = self.main_menu.addAction("Hakkında")
        about.triggered.connect(self._show_about)
        
        quit_action = self.main_menu.addAction("Çıkış")
        quit_action.setShortcut(SHORTCUTS['quit'])
        quit_action.triggered.connect(self.close)
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Tab navigation
        QShortcut(QKeySequence(SHORTCUTS['next_tab']), self, self._next_tab)
        QShortcut(QKeySequence(SHORTCUTS['prev_tab']), self, self._prev_tab)
        QShortcut(QKeySequence(SHORTCUTS['close_tab']), self, lambda: self.close_tab(self.tabs.currentIndex()))
        
        # Navigation
        QShortcut(QKeySequence(SHORTCUTS['address_bar']), self, self.toolbar.focus_address_bar)
        QShortcut(QKeySequence(SHORTCUTS['refresh']), self, self._reload_page)
        QShortcut(QKeySequence(SHORTCUTS['hard_refresh']), self, self._hard_reload)
        
        # Bookmark
        QShortcut(QKeySequence(SHORTCUTS['bookmark']), self, self._toggle_bookmark)
        
        # Escape to stop loading
        QShortcut(QKeySequence("Escape"), self, self._stop_loading)
    
    def _connect_signals(self):
        """Connect signals from managers and toolbar"""
        # Toolbar signals
        self.toolbar.back_clicked.connect(lambda: self._current_tab().back() if self._current_tab() else None)
        self.toolbar.forward_clicked.connect(lambda: self._current_tab().forward() if self._current_tab() else None)
        self.toolbar.reload_clicked.connect(self._reload_page)
        self.toolbar.stop_clicked.connect(self._stop_loading)
        self.toolbar.home_clicked.connect(self._go_home)
        self.toolbar.navigate_requested.connect(self._navigate_to)
        self.toolbar.new_tab_clicked.connect(lambda: self.add_new_tab())
        self.toolbar.private_tab_clicked.connect(lambda: self.add_new_tab(private=True))
        self.toolbar.bookmark_clicked.connect(self._toggle_bookmark)
        self.toolbar.menu_clicked.connect(self._show_menu)
        self.toolbar.downloads_clicked.connect(self._show_downloads)
        
        # Download manager signals
        self.engine.default_profile.downloadRequested.connect(self._handle_download)
        self.download_manager.download_completed.connect(
            lambda d: self.status_bar.show_message(f"İndirme tamamlandı: {d.filename}")
        )
        
        # Manager signals
        self.bookmark_manager.bookmarks_changed.connect(self._update_sidebar_bookmarks)
        self.history_manager.history_changed.connect(self._update_sidebar_history)
        self.download_manager.downloads_changed.connect(self._update_sidebar_downloads)
    
    def _apply_style(self):
        """Apply theme styling"""
        theme = DARK_THEME if self._dark_mode else LIGHT_THEME
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['bg_primary']};
            }}
            
            QTabWidget::pane {{
                border: none;
                background-color: {theme['bg_primary']};
            }}
            
            QTabBar {{
                background-color: {theme['bg_secondary']};
            }}
            
            QTabBar::tab {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 100px;
                max-width: 200px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {theme['bg_primary']};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {theme['bg_tertiary']};
            }}
            
            QTabBar::close-button {{
                image: none;
                subcontrol-origin: padding;
                subcontrol-position: right;
            }}
            
            QTabBar::close-button:hover {{
                background-color: {theme['error']};
                border-radius: 10px;
            }}
            
            QPushButton {{
                background-color: {theme['bg_tertiary']};
                border: none;
                border-radius: 6px;
                color: {theme['text_primary']};
                font-size: 16px;
            }}
            
            QPushButton:hover {{
                background-color: {theme['accent']};
                color: white;
            }}
        """)
        
        # Update components
        self.toolbar.set_dark_mode(self._dark_mode)
        self.sidebar.set_dark_mode(self._dark_mode)
        self.status_bar.set_dark_mode(self._dark_mode)
    
    # Tab Management
    def add_new_tab(self, url=None, private=False, switch_to=True):
        """Add a new browser tab"""
        if url is None:
            url = QUrl(self.settings_manager.homepage)
        elif isinstance(url, str):
            url = QUrl(url)
        
        # Create tab
        tab = BrowserTab(self, private=private, profile=self.engine.default_profile)
        tab.setUrl(url)
        
        # Add to tab widget
        title = "Gizli Sekme" if private else "Yeni Sekme"
        index = self.tabs.addTab(tab, title)
        
        # Style private tab
        if private:
            self.tabs.tabBar().setTabTextColor(index, QColor(DARK_THEME['private_tab'] if self._dark_mode else LIGHT_THEME['private_tab']))
        
        # Connect tab signals
        tab.titleChanged.connect(lambda title, t=tab: self._update_tab_title(t, title))
        tab.urlChanged.connect(lambda url, t=tab: self._on_url_changed(t, url))
        tab.loadStarted.connect(lambda t=tab: self._on_load_started(t))
        tab.loadProgress.connect(lambda p, t=tab: self._on_load_progress(t, p))
        tab.loadFinished.connect(lambda ok, t=tab: self._on_load_finished(t, ok))
        tab.iconChanged.connect(lambda icon, t=tab: self._update_tab_icon(t, icon))
        
        if switch_to:
            self.tabs.setCurrentIndex(index)
        
        return tab
    
    def close_tab(self, index):
        """Close a tab"""
        if self.tabs.count() <= 1:
            return
        
        tab = self.tabs.widget(index)
        
        # Save for reopening
        self._closed_tabs.append({
            'url': tab.url().toString(),
            'private': tab.private
        })
        
        # Remove and cleanup
        self.tabs.removeTab(index)
        tab.cleanup()
        tab.deleteLater()
    
    def _current_tab(self):
        """Get current tab"""
        return self.tabs.currentWidget()
    
    def _on_tab_changed(self, index):
        """Handle tab change"""
        if index < 0:
            return
        
        tab = self.tabs.widget(index)
        if not tab:
            return
        
        # Update toolbar
        self.toolbar.set_url(tab.url())
        self.toolbar.set_navigation_state(
            tab.history().canGoBack(),
            tab.history().canGoForward()
        )
        self.toolbar.set_security(tab.is_secure)
        self.toolbar.set_bookmarked(
            self.bookmark_manager.is_bookmarked(tab.url().toString())
        )
        
        # Update status bar
        self.status_bar.set_zoom(tab.get_zoom())
        self.status_bar.set_security(tab.is_secure)
        
        # Update window title
        self._update_window_title(tab.get_title())
    
    def _update_tab_title(self, tab, title):
        """Update tab title"""
        index = self.tabs.indexOf(tab)
        if index >= 0:
            display_title = truncate_text(title, 20)
            self.tabs.setTabText(index, display_title)
            self.tabs.setTabToolTip(index, title)
            
            if tab == self._current_tab():
                self._update_window_title(title)
    
    def _update_tab_icon(self, tab, icon):
        """Update tab favicon"""
        index = self.tabs.indexOf(tab)
        if index >= 0:
            self.tabs.setTabIcon(index, icon)
    
    def _update_window_title(self, title):
        """Update window title"""
        if title:
            self.setWindowTitle(f"{title} - {APP_NAME}")
        else:
            self.setWindowTitle(APP_NAME)
    
    def _next_tab(self):
        """Switch to next tab"""
        current = self.tabs.currentIndex()
        if current < self.tabs.count() - 1:
            self.tabs.setCurrentIndex(current + 1)
        else:
            self.tabs.setCurrentIndex(0)
    
    def _prev_tab(self):
        """Switch to previous tab"""
        current = self.tabs.currentIndex()
        if current > 0:
            self.tabs.setCurrentIndex(current - 1)
        else:
            self.tabs.setCurrentIndex(self.tabs.count() - 1)
    
    def _reopen_closed_tab(self):
        """Reopen last closed tab"""
        if self._closed_tabs:
            tab_info = self._closed_tabs.pop()
            self.add_new_tab(QUrl(tab_info['url']), private=tab_info['private'])
    
    # Navigation
    def _on_url_changed(self, tab, url):
        """Handle URL change"""
        if tab == self._current_tab():
            self.toolbar.set_url(url)
            self.toolbar.set_security(url.scheme() == 'https')
            self.toolbar.set_bookmarked(
                self.bookmark_manager.is_bookmarked(url.toString())
            )
            self.status_bar.set_security(url.scheme() == 'https')
    
    def _on_load_started(self, tab):
        """Handle load start"""
        if tab == self._current_tab():
            self.toolbar.set_loading(True)
    
    def _on_load_progress(self, tab, progress):
        """Handle load progress"""
        if tab == self._current_tab():
            self.status_bar.show_progress(progress)
    
    def _on_load_finished(self, tab, success):
        """Handle load finish"""
        if tab == self._current_tab():
            self.toolbar.set_loading(False)
            self.status_bar.hide_progress()
            self.toolbar.set_navigation_state(
                tab.history().canGoBack(),
                tab.history().canGoForward()
            )
        
        # Add to history
        if success and not tab.private:
            self.history_manager.add_entry(
                tab.url().toString(),
                tab.get_title()
            )
        
        # Inject element hiding CSS if ad blocker enabled
        if self.ad_blocker and self.ad_blocker.is_enabled():
            ElementHider.inject_element_hiding(tab)
        
        # Inject dark mode if enabled
        if self._dark_mode:
            tab.inject_dark_mode()
        
        # Update ad blocker count
        if self.ad_blocker:
            self.status_bar.set_blocked_count(self.ad_blocker.get_blocked_count())
    
    def _navigate_to(self, text):
        """Navigate to URL or search"""
        url, is_search = self.search_manager.process_input(text)
        if url:
            tab = self._current_tab()
            if tab:
                tab.setUrl(QUrl(url))
    
    def _reload_page(self):
        """Reload current page"""
        tab = self._current_tab()
        if tab:
            tab.reload()
    
    def _hard_reload(self):
        """Hard reload ignoring cache"""
        tab = self._current_tab()
        if tab:
            tab.reload_hard()
    
    def _stop_loading(self):
        """Stop page loading"""
        tab = self._current_tab()
        if tab:
            tab.stop()
    
    def _go_home(self):
        """Navigate to homepage"""
        tab = self._current_tab()
        if tab:
            tab.setUrl(QUrl(self.settings_manager.homepage))
    
    # Zoom
    def _zoom_in(self):
        """Zoom in"""
        tab = self._current_tab()
        if tab:
            zoom = tab.zoom_in()
            self.status_bar.set_zoom(zoom)
    
    def _zoom_out(self):
        """Zoom out"""
        tab = self._current_tab()
        if tab:
            zoom = tab.zoom_out()
            self.status_bar.set_zoom(zoom)
    
    def _reset_zoom(self):
        """Reset zoom"""
        tab = self._current_tab()
        if tab:
            zoom = tab.zoom_reset()
            self.status_bar.set_zoom(zoom)
    
    # Bookmarks
    def _toggle_bookmark(self):
        """Toggle bookmark for current page"""
        tab = self._current_tab()
        if not tab:
            return
        
        url = tab.url().toString()
        title = tab.get_title()
        
        if self.bookmark_manager.is_bookmarked(url):
            bookmark = self.bookmark_manager.get_bookmark_by_url(url)
            if bookmark:
                self.bookmark_manager.remove_bookmark(bookmark.id)
                self.toolbar.set_bookmarked(False)
                self.status_bar.show_message("Yer imi kaldırıldı")
        else:
            dialog = BookmarkDialog(self, title, url, dark_mode=self._dark_mode)
            dialog.saved.connect(self._save_bookmark)
            dialog.exec_()
    
    def _save_bookmark(self, title, url, folder):
        """Save a bookmark"""
        self.bookmark_manager.add_bookmark(url, title, folder)
        self.toolbar.set_bookmarked(True)
        self.status_bar.show_message("Yer imi eklendi")
    
    # Sidebar
    def _show_bookmarks(self):
        """Show bookmarks panel"""
        self._update_sidebar_bookmarks()
        self.sidebar.show_panel("bookmarks")
    
    def _show_history(self):
        """Show history panel"""
        self._update_sidebar_history()
        self.sidebar.show_panel("history")
    
    def _show_downloads(self):
        """Show downloads panel"""
        self._update_sidebar_downloads()
        self.sidebar.show_panel("downloads")
    
    def _update_sidebar_bookmarks(self):
        """Update sidebar bookmarks"""
        bookmarks = self.bookmark_manager.get_all_bookmarks()
        self.sidebar.update_bookmarks(bookmarks)
    
    def _update_sidebar_history(self):
        """Update sidebar history"""
        entries = self.history_manager.get_recent_entries(50)
        self.sidebar.update_history(entries)
    
    def _update_sidebar_downloads(self):
        """Update sidebar downloads"""
        downloads = self.download_manager.get_all_downloads()
        self.sidebar.update_downloads(downloads)
    
    def _clear_history(self):
        """Clear browsing history"""
        reply = QMessageBox.question(
            self, "Geçmişi Temizle",
            "Tüm tarama geçmişini silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.history_manager.clear_all()
            self.status_bar.show_message("Geçmiş temizlendi")
    
    # Downloads
    def _handle_download(self, download):
        """Handle download request"""
        self.download_manager.handle_download(download)
        self.status_bar.show_message(f"İndirme başladı: {download.suggestedFileName()}")
        self._update_sidebar_downloads()
    
    # Menu
    def _show_menu(self):
        """Show main menu"""
        self.main_menu.exec_(
            self.toolbar.menu_btn.mapToGlobal(
                self.toolbar.menu_btn.rect().bottomLeft()
            )
        )
    
    # Tools
    def _show_find_dialog(self):
        """Show find in page dialog"""
        if not self._find_dialog:
            self._find_dialog = FindDialog(self, self._dark_mode)
            self._find_dialog.find_requested.connect(self._find_text)
            self._find_dialog.find_next.connect(self._find_next)
            self._find_dialog.find_prev.connect(self._find_prev)
            self._find_dialog.closed.connect(self._clear_find)
        
        self._find_dialog.show()
        self._find_dialog.focus_search()
    
    def _find_text(self, text, case_sensitive, wrap):
        """Find text in page"""
        tab = self._current_tab()
        if tab:
            from PyQt5.QtWebEngineWidgets import QWebEnginePage
            flags = QWebEnginePage.FindFlags()
            if case_sensitive:
                flags |= QWebEnginePage.FindCaseSensitively
            tab.page().findText(text, flags)
    
    def _find_next(self):
        """Find next occurrence"""
        if self._find_dialog:
            text = self._find_dialog.search_input.text()
            self._find_text(text, self._find_dialog.case_check.isChecked(), True)
    
    def _find_prev(self):
        """Find previous occurrence"""
        tab = self._current_tab()
        if tab and self._find_dialog:
            from PyQt5.QtWebEngineWidgets import QWebEnginePage
            text = self._find_dialog.search_input.text()
            flags = QWebEnginePage.FindBackward
            if self._find_dialog.case_check.isChecked():
                flags |= QWebEnginePage.FindCaseSensitively
            tab.page().findText(text, flags)
    
    def _clear_find(self):
        """Clear find highlighting"""
        tab = self._current_tab()
        if tab:
            tab.page().findText("")
    
    def _toggle_reader_mode(self):
        """Toggle reader mode"""
        tab = self._current_tab()
        if tab:
            self.reader_mode.toggle(tab, self._dark_mode)
    
    def _take_screenshot(self):
        """Take page screenshot"""
        tab = self._current_tab()
        if not tab:
            return
        
        def save_screenshot(pixmap):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"screenshot_{timestamp}.png"
            
            path, _ = QFileDialog.getSaveFileName(
                self, "Ekran Görüntüsünü Kaydet",
                os.path.join(QStandardPaths.writableLocation(QStandardPaths.PicturesLocation), default_name),
                "PNG (*.png);;JPEG (*.jpg)"
            )
            
            if path:
                pixmap.save(path)
                self.status_bar.show_message(f"Ekran görüntüsü kaydedildi: {path}")
        
        tab.take_screenshot(save_screenshot)
    
    def _view_source(self):
        """View page source"""
        tab = self._current_tab()
        if not tab:
            return
        
        def show_source(html):
            # Open in new tab with data URL
            from PyQt5.QtCore import QByteArray
            import base64
            encoded = base64.b64encode(html.encode()).decode()
            self.add_new_tab(QUrl(f"data:text/plain;base64,{encoded}"))
        
        tab.get_page_source(show_source)
    
    def _open_dev_tools(self):
        """Open developer tools"""
        tab = self._current_tab()
        if tab:
            # Create dev tools page
            dev_page = tab.page().devToolsPage()
            if dev_page:
                self.add_new_tab(dev_page.url())
    
    def _print_page(self):
        """Print current page"""
        tab = self._current_tab()
        if not tab:
            return
        
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            tab.page().print(printer, lambda ok: None)
    
    # Settings
    def _show_settings(self):
        """Show settings dialog"""
        settings = {
            'homepage': self.settings_manager.homepage,
            'search_engine': self.settings_manager.search_engine,
            'dark_mode': self._dark_mode,
            'show_bookmarks_bar': self.settings_manager.show_bookmarks_bar,
            'show_status_bar': self.settings_manager.show_status_bar,
            'do_not_track': self.settings_manager.do_not_track,
            'save_passwords': self.settings_manager.save_passwords,
            'ad_blocker': self.settings_manager.ad_blocker_enabled,
            'javascript_enabled': self.settings_manager.javascript_enabled,
            'download_path': self.settings_manager.download_path
        }
        
        dialog = SettingsDialog(self, settings, self._dark_mode)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec_()
    
    def _apply_settings(self, settings):
        """Apply settings changes"""
        self.settings_manager.homepage = settings.get('homepage', DEFAULT_HOME_URL)
        self.settings_manager.search_engine = settings.get('search_engine', 'Google')
        
        # Dark mode
        if settings.get('dark_mode') != self._dark_mode:
            self._toggle_dark_mode()
        
        # Status bar
        self.status_bar.setVisible(settings.get('show_status_bar', True))
        self.settings_manager.show_status_bar = settings.get('show_status_bar', True)
        
        # Ad blocker
        self.settings_manager.ad_blocker_enabled = settings.get('ad_blocker', True)
        if self.ad_blocker:
            self.ad_blocker.set_enabled(settings.get('ad_blocker', True))
        
        # JavaScript
        self.settings_manager.javascript_enabled = settings.get('javascript_enabled', True)
        self.engine.set_javascript_enabled(settings.get('javascript_enabled', True))
        
        # Download path
        if settings.get('download_path'):
            self.settings_manager.download_path = settings.get('download_path')
            self.engine.set_download_path(settings.get('download_path'))
    
    def _toggle_dark_mode(self):
        """Toggle dark mode"""
        self._dark_mode = not self._dark_mode
        self.settings_manager.dark_mode = self._dark_mode
        self._apply_style()
        
        # Inject dark mode to all tabs
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab and self._dark_mode:
                tab.inject_dark_mode()
    
    def _toggle_ad_blocker(self):
        """Toggle ad blocker"""
        if self.ad_blocker:
            enabled = self.ad_blocker.toggle()
            self.settings_manager.ad_blocker_enabled = enabled
            status = "etkin" if enabled else "devre dışı"
            self.status_bar.show_message(f"Reklam engelleyici {status}")
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def _show_about(self):
        """Show about dialog"""
        dialog = AboutDialog(self, self._dark_mode)
        dialog.exec_()
    
    # Window events
    def closeEvent(self, event):
        """Handle window close"""
        if self.tabs.count() > 1 and self.settings_manager.warn_on_close_multiple:
            reply = QMessageBox.question(
                self, "Çıkış",
                f"{self.tabs.count()} sekme açık. Çıkmak istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        # Clear data on exit if enabled
        if self.settings_manager.clear_on_exit:
            self.engine.clear_all_data()
        
        # Cleanup
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab:
                tab.cleanup()
        
        event.accept()
