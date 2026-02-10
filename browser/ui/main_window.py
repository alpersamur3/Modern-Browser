import os
import base64
import html as html_module
import logging
from datetime import datetime

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QTabBar, QWidget,
                             QVBoxLayout, QHBoxLayout, QShortcut, QMenu,
                             QAction, QMessageBox, QFileDialog, QApplication,
                             QPushButton, QLabel, QProgressBar, QGraphicsOpacityEffect,
                             QFrame)
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from PyQt5.QtCore import (Qt, QUrl, pyqtSignal, QSize, QStandardPaths,
                           QTimer, QPropertyAnimation, QEasingCurve)
from PyQt5.QtGui import QKeySequence, QColor, QFont, QPalette
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
from ..utils.helpers import truncate_text, load_icon, load_themed_icon
from ..utils.i18n import _ as tr

log = logging.getLogger(__name__)


class DownloadToast(QWidget):
    open_downloads = pyqtSignal()

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.setWindowFlags(Qt.SubWindow)
        self.setFixedSize(340, 72)
        self._dark_mode = dark_mode
        self._entry = None
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._fade_out)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        top_row = QHBoxLayout()
        self.icon_label = QLabel()
        self.icon_label.setPixmap(load_themed_icon("download.svg", dark_mode).pixmap(18, 18))
        self.icon_label.setFixedSize(22, 22)
        top_row.addWidget(self.icon_label)

        self.text_label = QLabel(tr("Download started"))
        self.text_label.setObjectName("toastText")
        top_row.addWidget(self.text_label, 1)

        show_btn = QPushButton(tr("Show"))
        show_btn.setObjectName("toastBtn")
        show_btn.setCursor(Qt.PointingHandCursor)
        show_btn.setFixedHeight(24)
        show_btn.clicked.connect(self.open_downloads.emit)
        top_row.addWidget(show_btn)
        layout.addLayout(top_row)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self._apply_style()
        self.hide()

    def _apply_style(self):
        theme = DARK_THEME if self._dark_mode else LIGHT_THEME
        self.setStyleSheet(f"""
            DownloadToast {{
                background-color: {theme['card']};
                border: 1px solid {theme['border']};
                border-radius: 10px;
            }}
            #toastText {{
                color: {theme['text_primary']};
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 12px;
                font-weight: 500;
            }}
            #toastBtn {{
                background-color: {theme['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 2px 12px;
                font-size: 11px;
                font-weight: 600;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}
            #toastBtn:hover {{
                background-color: {theme['accent_light']};
            }}
            QProgressBar {{
                border: none;
                border-radius: 2px;
                background-color: {theme['bg_tertiary']};
            }}
            QProgressBar::chunk {{
                background-color: {theme['accent']};
                border-radius: 2px;
            }}
        """)

    def set_dark_mode(self, dark_mode):
        self._dark_mode = dark_mode
        self._apply_style()
        self.icon_label.setPixmap(load_themed_icon("download.svg", dark_mode).pixmap(18, 18))

    def show_download(self, entry):
        self._entry = entry
        name = entry.filename
        if len(name) > 30:
            name = name[:27] + "..."
        self.text_label.setText(f"{tr('Downloading')}: {name}")
        self.progress.setValue(0)
        self._reposition()
        self.show()
        self.raise_()
        self._hide_timer.stop()

    def update_progress(self, entry):
        if self._entry and self._entry.id == entry.id:
            self.progress.setValue(entry.progress)
            if entry.progress > 0:
                name = entry.filename
                if len(name) > 25:
                    name = name[:22] + "..."
                self.text_label.setText(f"{tr('Downloading')}: {name} (%{entry.progress})")

    def show_completed(self, entry):
        if self._entry and self._entry.id == entry.id:
            name = entry.filename
            if len(name) > 30:
                name = name[:27] + "..."
            self.text_label.setText(f"{tr('Completed')}: {name}")
            self.icon_label.setPixmap(load_icon("check-circle.svg", "#34a853").pixmap(18, 18))
            self.progress.setValue(100)
            self._hide_timer.start(4000)

    def _fade_out(self):
        self.hide()
        self.icon_label.setPixmap(load_themed_icon("download.svg", self._dark_mode).pixmap(18, 18))

    def _reposition(self):
        if self.parent():
            pr = self.parent().rect()
            x = pr.width() - self.width() - 16
            y = 60
            self.move(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition()


class ModernTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setExpanding(False)
        self.setElideMode(Qt.ElideRight)
        self.setDocumentMode(True)

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        size.setWidth(min(220, max(120, size.width())))
        size.setHeight(38)
        return size


class ModernTabWidget(QTabWidget):
    new_tab_requested = pyqtSignal()

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self._dark_mode = dark_mode
        self._tab_bar = ModernTabBar()
        self.setTabBar(self._tab_bar)

        self._add_btn = QPushButton()
        self._add_btn.setIcon(load_themed_icon("plus.svg", dark_mode))
        self._add_btn.setIconSize(QSize(16, 16))
        self._add_btn.setFixedSize(30, 30)
        self._add_btn.clicked.connect(self.new_tab_requested.emit)
        self._add_btn.setCursor(Qt.PointingHandCursor)
        self._add_btn.setObjectName("addTabBtn")
        self.setCornerWidget(self._add_btn, Qt.TopRightCorner)

    def set_dark_mode(self, dark_mode):
        self._dark_mode = dark_mode
        self._add_btn.setIcon(load_themed_icon("plus.svg", dark_mode))

    def contextMenuEvent(self, event):
        tab_bar = self.tabBar()
        index = tab_bar.tabAt(tab_bar.mapFromParent(event.pos()))
        if index < 0:
            return

        menu = QMenu(self)
        tab = self.widget(index)

        reload_action = menu.addAction(tr("Reload Tab"))
        reload_action.triggered.connect(lambda: tab.reload())

        duplicate_action = menu.addAction(tr("Duplicate Tab"))
        duplicate_action.triggered.connect(lambda: self._duplicate_tab(index))

        menu.addSeparator()

        pin_text = tr("Unpin Tab") if getattr(tab, 'is_pinned', False) else tr("Pin Tab")
        pin_action = menu.addAction(pin_text)
        pin_action.triggered.connect(lambda: self._toggle_pin(index))

        mute_text = tr("Unmute Tab") if getattr(tab, 'is_muted', False) else tr("Mute Tab")
        mute_action = menu.addAction(mute_text)
        mute_action.triggered.connect(lambda: self._toggle_mute(index))

        menu.addSeparator()

        close_action = menu.addAction(tr("Close Tab"))
        close_action.triggered.connect(lambda: self.tabCloseRequested.emit(index))

        close_others = menu.addAction(tr("Close Others"))
        close_others.triggered.connect(lambda: self._close_others(index))

        close_right = menu.addAction(tr("Close Tabs to Right"))
        close_right.triggered.connect(lambda: self._close_right(index))

        menu.exec_(event.globalPos())

    def _duplicate_tab(self, index):
        tab = self.widget(index)
        if tab and self.parent():
            main_win = self.parent()
            while main_win and not isinstance(main_win, MainWindow):
                main_win = main_win.parent()
            if main_win:
                main_win.add_new_tab(tab.url(), private=tab.private)

    def _toggle_pin(self, index):
        tab = self.widget(index)
        if tab:
            tab.toggle_pin()

    def _toggle_mute(self, index):
        tab = self.widget(index)
        if tab:
            tab.toggle_mute()

    def _close_others(self, keep_index):
        indices = [i for i in range(self.count()) if i != keep_index]
        for i in sorted(indices, reverse=True):
            self.tabCloseRequested.emit(i)

    def _close_right(self, index):
        indices = [i for i in range(index + 1, self.count())]
        for i in sorted(indices, reverse=True):
            self.tabCloseRequested.emit(i)


class MainWindow(QMainWindow):
    def __init__(self, private_mode=False):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.engine = BrowserEngine()
        self.bookmark_manager = BookmarkManager()
        self.history_manager = HistoryManager()
        self.download_manager = DownloadManager()
        self.search_manager = SearchManager()
        self.reader_mode = ReaderMode()

        self._dark_mode = self.settings_manager.dark_mode
        self._private_mode = private_mode
        self._closed_tabs = []
        self._find_dialog = None
        self._private_profile = None

        if self._private_mode:
            self._private_profile = self.engine.create_private_profile(self)

        self._setup_window()
        self._setup_ad_blocker()
        self._setup_ui()
        self._setup_menu()
        self._setup_shortcuts()
        self._connect_signals()
        self._apply_style()

        if self._private_mode:
            self.add_new_tab(QUrl(self.settings_manager.homepage), private=True)
        else:
            self.add_new_tab(QUrl(self.settings_manager.homepage))

    def _setup_window(self):
        if self._private_mode:
            self.setWindowTitle(f"{APP_NAME} — {tr('Private Browsing')}")
        else:
            self.setWindowTitle(APP_NAME)
        self.resize(1280, 800)
        self.setMinimumSize(800, 600)
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _setup_ad_blocker(self):
        if self.settings_manager.ad_blocker_enabled:
            self.ad_blocker = AdBlocker()
            self.engine.default_profile.setUrlRequestInterceptor(self.ad_blocker)
        else:
            self.ad_blocker = None

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar(dark_mode=self._dark_mode)
        self.sidebar.hide()
        self.sidebar.bookmark_clicked.connect(lambda url: self.add_new_tab(QUrl(url)))
        self.sidebar.history_clicked.connect(lambda url: self.add_new_tab(QUrl(url)))
        self.sidebar.download_open_clicked.connect(self.download_manager.open_file)
        self.sidebar.download_cancel_clicked.connect(self.download_manager.cancel_download)
        self.sidebar.clear_history_btn.clicked.connect(self._clear_history)
        main_layout.addWidget(self.sidebar)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.toolbar = BrowserToolbar(dark_mode=self._dark_mode)
        content_layout.addWidget(self.toolbar)

        # Private browsing banner
        if self._private_mode:
            self._private_banner = QFrame()
            self._private_banner.setObjectName("privateBanner")
            banner_layout = QHBoxLayout(self._private_banner)
            banner_layout.setContentsMargins(12, 6, 12, 6)
            banner_layout.setSpacing(8)
            banner_icon = QLabel()
            banner_icon.setPixmap(load_themed_icon("eye-off.svg", True).pixmap(18, 18))
            banner_icon.setFixedSize(22, 22)
            banner_layout.addWidget(banner_icon)
            banner_text = QLabel(tr("You are in a private window. Pages you visit will not be saved in your history."))
            banner_text.setObjectName("privateBannerText")
            banner_text.setFont(QFont("Segoe UI", 10))
            banner_layout.addWidget(banner_text, 1)
            content_layout.addWidget(self._private_banner)

        self.tabs = ModernTabWidget(dark_mode=self._dark_mode)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.tabs.new_tab_requested.connect(lambda: self.add_new_tab())
        content_layout.addWidget(self.tabs)

        main_layout.addWidget(content_widget)

        self.status_bar = StatusBar(dark_mode=self._dark_mode)
        self.setStatusBar(self.status_bar)
        self.status_bar.zoom_clicked.connect(self._reset_zoom)
        self.status_bar.ad_blocker_clicked.connect(self._toggle_ad_blocker)

        self.download_toast = DownloadToast(self, dark_mode=self._dark_mode)
        self.download_toast.open_downloads.connect(self._show_downloads)

    def _setup_menu(self):
        self.main_menu = QMenu(self)

        new_tab = self.main_menu.addAction(tr("New Tab"))
        new_tab.setShortcut(SHORTCUTS['new_tab'])
        new_tab.triggered.connect(lambda: self.add_new_tab())

        new_window = self.main_menu.addAction(tr("New Window"))
        new_window.setShortcut(SHORTCUTS['new_window'])
        new_window.triggered.connect(self._open_new_window)

        new_private = self.main_menu.addAction(tr("New Private Window"))
        new_private.setShortcut(SHORTCUTS['private_tab'])
        new_private.triggered.connect(self._open_private_window)

        reopen_tab = self.main_menu.addAction(tr("Reopen Closed Tab"))
        reopen_tab.setShortcut(SHORTCUTS['reopen_tab'])
        reopen_tab.triggered.connect(self._reopen_closed_tab)

        self.main_menu.addSeparator()

        self.main_menu.addAction(tr("History"), self._show_history).setShortcut(SHORTCUTS['history_panel'])
        self.main_menu.addAction(tr("Bookmarks"), self._show_bookmarks).setShortcut(SHORTCUTS['bookmarks_panel'])
        self.main_menu.addAction(tr("Downloads"), self._show_downloads).setShortcut(SHORTCUTS['downloads_panel'])

        self.main_menu.addSeparator()

        view_menu = self.main_menu.addMenu(tr("View"))
        zoom_in = view_menu.addAction(tr("Zoom In"))
        zoom_in.setShortcut(SHORTCUTS['zoom_in'])
        zoom_in.triggered.connect(self._zoom_in)
        zoom_out = view_menu.addAction(tr("Zoom Out"))
        zoom_out.setShortcut(SHORTCUTS['zoom_out'])
        zoom_out.triggered.connect(self._zoom_out)
        zoom_reset = view_menu.addAction(tr("Reset Zoom"))
        zoom_reset.setShortcut(SHORTCUTS['zoom_reset'])
        zoom_reset.triggered.connect(self._reset_zoom)
        view_menu.addSeparator()
        fullscreen = view_menu.addAction(tr("Fullscreen"))
        fullscreen.setShortcut(SHORTCUTS['fullscreen'])
        fullscreen.triggered.connect(self._toggle_fullscreen)

        tools_menu = self.main_menu.addMenu(tr("Tools"))
        find = tools_menu.addAction(tr("Find in Page"))
        find.setShortcut(SHORTCUTS['find'])
        find.triggered.connect(self._show_find_dialog)
        tools_menu.addSeparator()
        reader = tools_menu.addAction(tr("Reader Mode"))
        reader.setShortcut(SHORTCUTS['reader_mode'])
        reader.triggered.connect(self._toggle_reader_mode)
        screenshot = tools_menu.addAction(tr("Screenshot"))
        screenshot.setShortcut(SHORTCUTS['screenshot'])
        screenshot.triggered.connect(self._take_screenshot)
        tools_menu.addSeparator()
        view_source = tools_menu.addAction(tr("View Source"))
        view_source.setShortcut(SHORTCUTS['view_source'])
        view_source.triggered.connect(self._view_source)
        dev_tools = tools_menu.addAction(tr("Developer Tools"))
        dev_tools.setShortcut(SHORTCUTS['dev_tools'])
        dev_tools.triggered.connect(self._open_dev_tools)
        tools_menu.addSeparator()
        print_page = tools_menu.addAction(tr("Print"))
        print_page.setShortcut(SHORTCUTS['print'])
        print_page.triggered.connect(self._print_page)

        self.main_menu.addSeparator()

        dark_mode = self.main_menu.addAction(tr("Dark Mode"))
        dark_mode.setCheckable(True)
        dark_mode.setChecked(self._dark_mode)
        dark_mode.triggered.connect(self._toggle_dark_mode)

        settings = self.main_menu.addAction(tr("Settings"))
        settings.setShortcut(SHORTCUTS['settings'])
        settings.triggered.connect(self._show_settings)

        self.main_menu.addSeparator()

        about = self.main_menu.addAction(tr("About"))
        about.triggered.connect(self._show_about)

        quit_action = self.main_menu.addAction(tr("Quit"))
        quit_action.setShortcut(SHORTCUTS['quit'])
        quit_action.triggered.connect(self.close)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence(SHORTCUTS['next_tab']), self, self._next_tab)
        QShortcut(QKeySequence(SHORTCUTS['prev_tab']), self, self._prev_tab)
        QShortcut(QKeySequence(SHORTCUTS['close_tab']), self, lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence(SHORTCUTS['address_bar']), self, self.toolbar.focus_address_bar)
        QShortcut(QKeySequence(SHORTCUTS['refresh']), self, self._reload_page)
        QShortcut(QKeySequence(SHORTCUTS['hard_refresh']), self, self._hard_reload)
        QShortcut(QKeySequence(SHORTCUTS['bookmark']), self, self._toggle_bookmark)
        QShortcut(QKeySequence("Escape"), self, self._stop_loading)

    def _connect_signals(self):
        self.toolbar.back_clicked.connect(lambda: self._current_tab().back() if self._current_tab() else None)
        self.toolbar.forward_clicked.connect(lambda: self._current_tab().forward() if self._current_tab() else None)
        self.toolbar.reload_clicked.connect(self._reload_page)
        self.toolbar.stop_clicked.connect(self._stop_loading)
        self.toolbar.home_clicked.connect(self._go_home)
        self.toolbar.navigate_requested.connect(self._navigate_to)
        self.toolbar.new_tab_clicked.connect(lambda: self.add_new_tab())
        self.toolbar.new_window_clicked.connect(self._open_new_window)
        self.toolbar.private_tab_clicked.connect(self._open_private_window)
        self.toolbar.bookmark_clicked.connect(self._toggle_bookmark)
        self.toolbar.menu_clicked.connect(self._show_menu)
        self.toolbar.downloads_clicked.connect(self._show_downloads)

        self.engine.default_profile.downloadRequested.connect(self._handle_download)
        if self._private_profile:
            self._private_profile.downloadRequested.connect(self._handle_download)
        self.download_manager.download_started.connect(
            lambda d: self.download_toast.show_download(d)
        )
        self.download_manager.download_progress.connect(
            lambda d: self.download_toast.update_progress(d)
        )
        self.download_manager.download_completed.connect(
            lambda d: (self.download_toast.show_completed(d),
                       self.status_bar.show_message(f"{tr('Download completed')}: {d.filename}"))
        )
        self.download_manager.download_failed.connect(
            lambda d: self.status_bar.show_message(f"{tr('Download failed')}: {d.filename}")
        )

        self.bookmark_manager.bookmarks_changed.connect(self._update_sidebar_bookmarks)
        self.history_manager.history_changed.connect(self._update_sidebar_history)
        self.download_manager.downloads_changed.connect(self._update_sidebar_downloads)

    def _apply_style(self):
        theme = DARK_THEME if self._dark_mode else LIGHT_THEME
        close_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resources", "icons", "x.svg").replace("\\", "/")

        private_style = ""
        if self._private_mode:
            private_style = f"""
            #privateBanner {{
                background-color: {theme['private_tab']};
                border: none;
                min-height: 32px;
            }}
            #privateBannerText {{
                color: #ffffff;
                font-size: 12px;
            }}
            """

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
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 13px;
            }}
            QTabBar::tab {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                padding: 8px 16px;
                margin-right: 1px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                min-width: 120px;
                max-width: 220px;
            }}
            QTabBar::tab:selected {{
                background-color: {theme['bg_primary']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {theme['bg_tertiary']};
            }}
            QTabBar::close-button {{
                image: url({close_icon_path});
                subcontrol-origin: padding;
                subcontrol-position: right;
                padding: 4px;
                border-radius: 4px;
                width: 12px;
                height: 12px;
            }}
            QTabBar::close-button:hover {{
                background-color: {theme['error']};
            }}
            #addTabBtn {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
            }}
            #addTabBtn:hover {{
                background-color: {theme['bg_hover']};
            }}
            QMenu {{
                background-color: {theme['bg_primary']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 4px;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 6px;
            }}
            QMenu::item:selected {{
                background-color: {theme['accent']};
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {theme['border']};
                margin: 4px 8px;
            }}
            {private_style}
        """)

        self.toolbar.set_dark_mode(self._dark_mode)
        self.sidebar.set_dark_mode(self._dark_mode)
        self.status_bar.set_dark_mode(self._dark_mode)
        self.download_toast.set_dark_mode(self._dark_mode)
        self.tabs.set_dark_mode(self._dark_mode)

    # ---- Tab Management ----
    def add_new_tab(self, url=None, private=False, switch_to=True):
        # In private window, all tabs are private
        if self._private_mode:
            private = True

        if url is None:
            url = QUrl(self.settings_manager.homepage)
        elif isinstance(url, str):
            url = QUrl(url)

        profile = self._private_profile if private and self._private_profile else self.engine.default_profile
        tab = BrowserTab(self, private=private, profile=profile)
        tab.setUrl(url)

        title = tr("Private Tab") if private else tr("New Tab")
        index = self.tabs.addTab(tab, title)

        if private:
            color = DARK_THEME['private_tab'] if self._dark_mode else LIGHT_THEME['private_tab']
            self.tabs.tabBar().setTabTextColor(index, QColor(color))
            private_icon = load_icon("eye-off.svg", color)
            self.tabs.setTabIcon(index, private_icon)

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
        if self.tabs.count() <= 1:
            return
        tab = self.tabs.widget(index)
        if tab.is_pinned:
            return
        self._closed_tabs.append({'url': tab.url().toString(), 'private': tab.private})
        self.tabs.removeTab(index)
        tab.cleanup()
        tab.deleteLater()

    def _current_tab(self):
        return self.tabs.currentWidget()

    def _on_tab_changed(self, index):
        if index < 0:
            return
        tab = self.tabs.widget(index)
        if not tab:
            return
        self.toolbar.set_url(tab.url())
        self.toolbar.set_navigation_state(tab.history().canGoBack(), tab.history().canGoForward())
        self.toolbar.set_security(tab.is_secure)
        self.toolbar.set_bookmarked(self.bookmark_manager.is_bookmarked(tab.url().toString()))
        self.status_bar.set_zoom(tab.get_zoom())
        self.status_bar.set_security(tab.is_secure)
        self._update_window_title(tab.get_title())

    def _update_tab_title(self, tab, title):
        index = self.tabs.indexOf(tab)
        if index >= 0:
            self.tabs.setTabText(index, truncate_text(title, 20))
            self.tabs.setTabToolTip(index, title)
            if tab == self._current_tab():
                self._update_window_title(title)

    def _update_tab_icon(self, tab, icon):
        index = self.tabs.indexOf(tab)
        if index >= 0:
            self.tabs.setTabIcon(index, icon)

    def _update_window_title(self, title):
        suffix = f" — {tr('Private Browsing')}" if self._private_mode else ""
        self.setWindowTitle(f"{title} - {APP_NAME}{suffix}" if title else f"{APP_NAME}{suffix}")

    def _next_tab(self):
        current = self.tabs.currentIndex()
        self.tabs.setCurrentIndex((current + 1) % self.tabs.count())

    def _prev_tab(self):
        current = self.tabs.currentIndex()
        self.tabs.setCurrentIndex((current - 1) % self.tabs.count())

    def _reopen_closed_tab(self):
        if self._closed_tabs:
            info = self._closed_tabs.pop()
            self.add_new_tab(QUrl(info['url']), private=info['private'])

    # ---- Navigation ----
    def _on_url_changed(self, tab, url):
        if tab == self._current_tab():
            self.toolbar.set_url(url)
            self.toolbar.set_security(url.scheme() == 'https')
            self.toolbar.set_bookmarked(self.bookmark_manager.is_bookmarked(url.toString()))
            self.status_bar.set_security(url.scheme() == 'https')

    def _on_load_started(self, tab):
        if tab == self._current_tab():
            self.toolbar.set_loading(True)

    def _on_load_progress(self, tab, progress):
        if tab == self._current_tab():
            self.status_bar.show_progress(progress)

    def _on_load_finished(self, tab, success):
        if tab == self._current_tab():
            self.toolbar.set_loading(False)
            self.status_bar.hide_progress()
            self.toolbar.set_navigation_state(tab.history().canGoBack(), tab.history().canGoForward())

        if success and not tab.private:
            self.history_manager.add_entry(tab.url().toString(), tab.get_title())

        if self.ad_blocker and self.ad_blocker.is_enabled():
            ElementHider.inject_element_hiding(tab)

        if self._dark_mode:
            tab.inject_dark_mode()

        if self.ad_blocker:
            self.status_bar.set_blocked_count(self.ad_blocker.get_blocked_count())

    def _navigate_to(self, text):
        url, is_search = self.search_manager.process_input(text)
        if url:
            tab = self._current_tab()
            if tab:
                tab.setUrl(QUrl(url))

    def _reload_page(self):
        tab = self._current_tab()
        if tab:
            tab.reload()

    def _hard_reload(self):
        tab = self._current_tab()
        if tab:
            tab.reload_hard()

    def _stop_loading(self):
        tab = self._current_tab()
        if tab:
            tab.stop()

    def _go_home(self):
        tab = self._current_tab()
        if tab:
            tab.setUrl(QUrl(self.settings_manager.homepage))

    # ---- Zoom ----
    def _zoom_in(self):
        tab = self._current_tab()
        if tab:
            self.status_bar.set_zoom(tab.zoom_in())

    def _zoom_out(self):
        tab = self._current_tab()
        if tab:
            self.status_bar.set_zoom(tab.zoom_out())

    def _reset_zoom(self):
        tab = self._current_tab()
        if tab:
            self.status_bar.set_zoom(tab.zoom_reset())

    # ---- Bookmarks ----
    def _toggle_bookmark(self):
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
                self.status_bar.show_message(tr("Bookmark removed"))
        else:
            dialog = BookmarkDialog(self, title, url, dark_mode=self._dark_mode)
            dialog.saved.connect(self._save_bookmark)
            dialog.exec_()

    def _save_bookmark(self, title, url, folder):
        self.bookmark_manager.add_bookmark(url, title, folder)
        self.toolbar.set_bookmarked(True)
        self.status_bar.show_message(tr("Bookmark added"))

    # ---- Sidebar ----
    def _show_bookmarks(self):
        self._update_sidebar_bookmarks()
        self.sidebar.show_panel("bookmarks")

    def _show_history(self):
        self._update_sidebar_history()
        self.sidebar.show_panel("history")

    def _show_downloads(self):
        self._update_sidebar_downloads()
        self.sidebar.show_panel("downloads")

    def _update_sidebar_bookmarks(self):
        self.sidebar.update_bookmarks(self.bookmark_manager.get_all_bookmarks())

    def _update_sidebar_history(self):
        self.sidebar.update_history(self.history_manager.get_recent_entries(50))

    def _update_sidebar_downloads(self):
        self.sidebar.update_downloads(self.download_manager.get_all_downloads())

    def _clear_history(self):
        reply = QMessageBox.question(
            self, tr("Clear History"),
            tr("Are you sure you want to clear all browsing history?"),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.history_manager.clear_all()
            self.status_bar.show_message(tr("History cleared"))

    # ---- Downloads ----
    def _handle_download(self, download):
        self.download_manager.handle_download(download)
        self.status_bar.show_message(f"{tr('Download started')}: {download.suggestedFileName()}")
        self._update_sidebar_downloads()

    # ---- Menu ----
    def _show_menu(self):
        self.main_menu.exec_(
            self.toolbar.menu_btn.mapToGlobal(self.toolbar.menu_btn.rect().bottomLeft())
        )

    # ---- Tools ----
    def _show_find_dialog(self):
        if not self._find_dialog:
            self._find_dialog = FindDialog(self, self._dark_mode)
            self._find_dialog.find_requested.connect(self._find_text)
            self._find_dialog.find_next.connect(self._find_next)
            self._find_dialog.find_prev.connect(self._find_prev)
            self._find_dialog.closed.connect(self._clear_find)
        self._find_dialog.show()
        self._find_dialog.focus_search()

    def _find_text(self, text, case_sensitive, wrap):
        tab = self._current_tab()
        if tab:
            from PyQt5.QtWebEngineWidgets import QWebEnginePage
            flags = QWebEnginePage.FindFlags()
            if case_sensitive:
                flags |= QWebEnginePage.FindCaseSensitively
            tab.page().findText(text, flags)

    def _find_next(self):
        if self._find_dialog:
            text = self._find_dialog.search_input.text()
            self._find_text(text, self._find_dialog.case_check.isChecked(), True)

    def _find_prev(self):
        tab = self._current_tab()
        if tab and self._find_dialog:
            from PyQt5.QtWebEngineWidgets import QWebEnginePage
            text = self._find_dialog.search_input.text()
            flags = QWebEnginePage.FindBackward
            if self._find_dialog.case_check.isChecked():
                flags |= QWebEnginePage.FindCaseSensitively
            tab.page().findText(text, flags)

    def _clear_find(self):
        tab = self._current_tab()
        if tab:
            tab.page().findText("")

    def _toggle_reader_mode(self):
        tab = self._current_tab()
        if tab:
            self.reader_mode.toggle(tab, self._dark_mode)

    def _take_screenshot(self):
        tab = self._current_tab()
        if not tab:
            return
        def save_screenshot(pixmap):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"screenshot_{timestamp}.png"
            path, _ = QFileDialog.getSaveFileName(
                self, tr("Save Screenshot"),
                os.path.join(QStandardPaths.writableLocation(QStandardPaths.PicturesLocation), default_name),
                "PNG (*.png);;JPEG (*.jpg)"
            )
            if path:
                pixmap.save(path)
                self.status_bar.show_message(f"{tr('Screenshot saved')}: {path}")
        tab.take_screenshot(save_screenshot)

    def _view_source(self):
        tab = self._current_tab()
        if not tab:
            return
        source_url = tab.url().toString()
        def show_source(html_content):
            escaped = html_module.escape(html_content)
            source_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{tr('Page Source')} - {html_module.escape(source_url)}</title>
<style>
body {{ background: #1e1e2e; color: #cdd6f4; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; padding: 16px; margin: 0; white-space: pre-wrap; word-wrap: break-word; line-height: 1.6; }}
</style></head><body><pre>{escaped}</pre></body></html>"""
            encoded = base64.b64encode(source_html.encode('utf-8')).decode('ascii')
            self.add_new_tab(QUrl(f"data:text/html;base64,{encoded}"))
        tab.get_page_source(show_source)

    def _open_dev_tools(self):
        tab = self._current_tab()
        if tab:
            tab.open_dev_tools()

    def _print_page(self):
        tab = self._current_tab()
        if not tab:
            return
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            tab.page().print(printer, lambda ok: None)

    # ---- Settings ----
    def _show_settings(self):
        settings = {
            'homepage': self.settings_manager.homepage,
            'search_engine': self.settings_manager.search_engine,
            'language': self.settings_manager.language,
            'dark_mode': self._dark_mode,
            'show_bookmarks_bar': self.settings_manager.show_bookmarks_bar,
            'show_status_bar': self.settings_manager.show_status_bar,
            'do_not_track': self.settings_manager.do_not_track,
            'save_passwords': self.settings_manager.save_passwords,
            'ad_blocker': self.settings_manager.ad_blocker_enabled,
            'javascript_enabled': self.settings_manager.javascript_enabled,
            'download_path': self.settings_manager.download_path,
        }
        dialog = SettingsDialog(self, settings, self._dark_mode)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec_()

    def _apply_settings(self, settings):
        self.settings_manager.homepage = settings.get('homepage', DEFAULT_HOME_URL)
        self.settings_manager.search_engine = settings.get('search_engine', 'Google')
        # Handle language change
        new_lang = settings.get('language')
        if new_lang and new_lang != self.settings_manager.language:
            self.settings_manager.language = new_lang
            from ..utils.i18n import set_language
            set_language(new_lang)
            # Rebuild menu and toolbar to reflect new language
            self._rebuild_ui_language()
        if settings.get('dark_mode') != self._dark_mode:
            self._toggle_dark_mode()
        self.status_bar.setVisible(settings.get('show_status_bar', True))
        self.settings_manager.show_status_bar = settings.get('show_status_bar', True)
        self.settings_manager.ad_blocker_enabled = settings.get('ad_blocker', True)
        if self.ad_blocker:
            self.ad_blocker.set_enabled(settings.get('ad_blocker', True))
        self.settings_manager.javascript_enabled = settings.get('javascript_enabled', True)
        self.engine.set_javascript_enabled(settings.get('javascript_enabled', True))
        if settings.get('download_path'):
            self.settings_manager.download_path = settings.get('download_path')
            self.engine.set_download_path(settings.get('download_path'))

    def _toggle_dark_mode(self):
        self._dark_mode = not self._dark_mode
        self.settings_manager.dark_mode = self._dark_mode
        self._apply_style()
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab and self._dark_mode:
                tab.inject_dark_mode()

    def _rebuild_ui_language(self):
        """Rebuild menu and toolbar tooltips to reflect language change."""
        # Rebuild the main menu
        self.main_menu.clear()
        self._setup_menu()

        # Update toolbar tooltips
        self.toolbar.back_btn.setToolTip(tr("Back"))
        self.toolbar.forward_btn.setToolTip(tr("Forward"))
        self.toolbar.reload_btn.setToolTip(tr("Reload"))
        self.toolbar.home_btn.setToolTip(tr("Home"))
        self.toolbar.new_tab_btn.setToolTip(tr("New Tab"))
        self.toolbar.new_window_btn.setToolTip(tr("New Window"))
        self.toolbar.private_btn.setToolTip(tr("New Private Window"))
        self.toolbar.bookmark_btn.setToolTip(tr("Bookmark"))
        self.toolbar.downloads_btn.setToolTip(tr("Downloads"))
        self.toolbar.menu_btn.setToolTip(tr("Menu"))
        self.toolbar.address_bar.setPlaceholderText(tr("Search or enter URL..."))

        # Update sidebar nav tooltips
        self.sidebar.bookmarks_btn.setToolTip(tr("Bookmarks"))
        self.sidebar.history_btn.setToolTip(tr("History"))
        self.sidebar.downloads_btn.setToolTip(tr("Downloads"))

        # Update status bar tooltips
        self.status_bar.zoom_btn.setToolTip(tr("Reset Zoom"))
        self.status_bar.security_label.setToolTip(tr("Security"))
        self.status_bar.ad_block_btn.setToolTip(tr("Ad blocker"))

        # Update window title
        tab = self._current_tab()
        if tab:
            self._update_window_title(tab.get_title())

    def _toggle_ad_blocker(self):
        if self.ad_blocker:
            enabled = self.ad_blocker.toggle()
            self.settings_manager.ad_blocker_enabled = enabled
            status = tr("Ad blocker enabled") if enabled else tr("Ad blocker disabled")
            self.status_bar.show_message(status)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _open_new_window(self):
        """Open a new regular browser window."""
        new_win = MainWindow(private_mode=False)
        new_win.show()

    def _open_private_window(self):
        """Open a new private/incognito browser window."""
        new_win = MainWindow(private_mode=True)
        new_win.show()

    def _show_about(self):
        dialog = AboutDialog(self, self._dark_mode)
        dialog.exec_()

    # ---- Window Events ----
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'download_toast'):
            self.download_toast._reposition()

    def closeEvent(self, event):
        if self.tabs.count() > 1 and self.settings_manager.warn_on_close_multiple:
            reply = QMessageBox.question(
                self, tr("Quit"),
                f"{self.tabs.count()} {tr('tabs are open. Are you sure you want to quit?')}",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        if self.settings_manager.clear_on_exit:
            self.engine.clear_all_data()
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab:
                tab.cleanup()
        event.accept()
