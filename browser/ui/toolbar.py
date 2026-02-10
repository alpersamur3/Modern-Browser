import logging

from PyQt5.QtWidgets import (QToolBar, QWidget, QHBoxLayout, QLineEdit,
                             QCompleter, QToolButton, QSizePolicy, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal, QStringListModel, QUrl, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon
from ..utils.constants import LIGHT_THEME, DARK_THEME
from ..utils.helpers import load_icon, load_themed_icon
from ..utils.i18n import _ as tr

log = logging.getLogger(__name__)


class AddressBar(QLineEdit):
    return_pressed = pyqtSignal(str)
    focus_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(tr("Search or enter URL..."))
        self._setup_completer()

    def _setup_completer(self):
        self.completer_model = QStringListModel()
        completer = QCompleter(self.completer_model)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.setCompleter(completer)

    def update_suggestions(self, suggestions):
        self.completer_model.setStringList(suggestions)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.selectAll()
        self.focus_changed.emit(True)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.focus_changed.emit(False)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.return_pressed.emit(self.text())
        else:
            super().keyPressEvent(event)


class NavButton(QToolButton):
    def __init__(self, icon_name, tooltip="", parent=None, dark_mode=False):
        super().__init__(parent)
        self._icon_name = icon_name
        self.setIcon(load_themed_icon(icon_name, dark_mode))
        self.setIconSize(QSize(18, 18))
        self.setToolTip(tooltip)
        self.setFixedSize(36, 36)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("navButton")

    def update_theme(self, dark_mode):
        self.setIcon(load_themed_icon(self._icon_name, dark_mode))


class BrowserToolbar(QToolBar):
    back_clicked = pyqtSignal()
    forward_clicked = pyqtSignal()
    reload_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    home_clicked = pyqtSignal()
    navigate_requested = pyqtSignal(str)
    new_tab_clicked = pyqtSignal()
    new_window_clicked = pyqtSignal()
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
        self.setMovable(False)
        self.setFloatable(False)
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        self.setFixedHeight(52)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        self.back_btn = NavButton("arrow-left.svg", f"{tr('Back')} (Alt+Left)", dark_mode=self.dark_mode)
        self.back_btn.clicked.connect(self.back_clicked.emit)
        layout.addWidget(self.back_btn)

        self.forward_btn = NavButton("arrow-right.svg", f"{tr('Forward')} (Alt+Right)", dark_mode=self.dark_mode)
        self.forward_btn.clicked.connect(self.forward_clicked.emit)
        layout.addWidget(self.forward_btn)

        self.reload_btn = NavButton("refresh-cw.svg", f"{tr('Reload')} (F5)", dark_mode=self.dark_mode)
        self.reload_btn.clicked.connect(self._on_reload_click)
        layout.addWidget(self.reload_btn)

        self.home_btn = NavButton("home.svg", tr("Home"), dark_mode=self.dark_mode)
        self.home_btn.clicked.connect(self.home_clicked.emit)
        layout.addWidget(self.home_btn)

        layout.addSpacing(6)

        self.security_icon = QLabel()
        self.security_icon.setFixedSize(22, 22)
        self.security_icon.setAlignment(Qt.AlignCenter)
        self.security_icon.setPixmap(load_themed_icon("lock.svg", self.dark_mode).pixmap(16, 16))
        layout.addWidget(self.security_icon)

        self.address_bar = AddressBar()
        self.address_bar.return_pressed.connect(self.navigate_requested.emit)
        self.address_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.address_bar.setFixedHeight(36)
        layout.addWidget(self.address_bar)

        self.bookmark_btn = NavButton("star.svg", f"{tr('Add Bookmark')} (Ctrl+D)", dark_mode=self.dark_mode)
        self.bookmark_btn.clicked.connect(self.bookmark_clicked.emit)
        layout.addWidget(self.bookmark_btn)

        layout.addSpacing(6)

        self.downloads_btn = NavButton("download.svg", f"{tr('Downloads')} (Ctrl+J)", dark_mode=self.dark_mode)
        self.downloads_btn.clicked.connect(self.downloads_clicked.emit)
        layout.addWidget(self.downloads_btn)

        self.new_tab_btn = NavButton("plus.svg", f"{tr('New Tab')} (Ctrl+T)", dark_mode=self.dark_mode)
        self.new_tab_btn.clicked.connect(self.new_tab_clicked.emit)
        layout.addWidget(self.new_tab_btn)

        self.new_window_btn = NavButton("maximize.svg", f"{tr('New Window')} (Ctrl+N)", dark_mode=self.dark_mode)
        self.new_window_btn.clicked.connect(self.new_window_clicked.emit)
        layout.addWidget(self.new_window_btn)

        self.private_btn = NavButton("eye-off.svg", f"{tr('New Private Window')} (Ctrl+Shift+N)", dark_mode=self.dark_mode)
        self.private_btn.clicked.connect(self.private_tab_clicked.emit)
        layout.addWidget(self.private_btn)

        self.menu_btn = NavButton("menu.svg", tr("Settings"), dark_mode=self.dark_mode)
        self.menu_btn.clicked.connect(self.menu_clicked.emit)
        layout.addWidget(self.menu_btn)

        self.addWidget(container)

    def _apply_style(self):
        theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        self.setStyleSheet(f"""
            QToolBar {{
                background-color: {theme['bg_primary']};
                border: none;
                border-bottom: 1px solid {theme['border']};
            }}
            #navButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
            }}
            #navButton:hover {{
                background-color: {theme['bg_hover']};
            }}
            #navButton:pressed {{
                background-color: {theme['bg_tertiary']};
            }}
            #navButton:disabled {{
                opacity: 0.4;
            }}
            QLineEdit {{
                background-color: {theme['bg_secondary']};
                border: 2px solid {theme['border']};
                border-radius: 18px;
                padding: 0 16px;
                font-size: 14px;
                color: {theme['text_primary']};
                selection-background-color: {theme['accent']};
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}
            QLineEdit:focus {{
                border-color: {theme['accent']};
                background-color: {theme['bg_primary']};
            }}
        """)

    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
        self._apply_style()
        self._update_icons()

    def _update_icons(self):
        for btn in [self.back_btn, self.forward_btn, self.reload_btn,
                    self.home_btn, self.bookmark_btn, self.downloads_btn,
                    self.new_tab_btn, self.new_window_btn, self.private_btn, self.menu_btn]:
            btn.update_theme(self.dark_mode)
        self.security_icon.setPixmap(
            load_themed_icon("lock.svg", self.dark_mode).pixmap(16, 16)
        )

    def _on_reload_click(self):
        if self._is_loading:
            self.stop_clicked.emit()
        else:
            self.reload_clicked.emit()

    def set_loading(self, loading):
        self._is_loading = loading
        if loading:
            self.reload_btn._icon_name = "x.svg"
            self.reload_btn.setIcon(load_themed_icon("x.svg", self.dark_mode))
            self.reload_btn.setToolTip(f"{tr('Stop')} (Esc)")
        else:
            self.reload_btn._icon_name = "refresh-cw.svg"
            self.reload_btn.setIcon(load_themed_icon("refresh-cw.svg", self.dark_mode))
            self.reload_btn.setToolTip(f"{tr('Reload')} (F5)")

    def set_url(self, url):
        if isinstance(url, QUrl):
            url = url.toString()
        self.address_bar.setText(url)
        self.address_bar.setCursorPosition(0)

    def get_url(self):
        return self.address_bar.text()

    def focus_address_bar(self):
        self.address_bar.setFocus()
        self.address_bar.selectAll()

    def set_security(self, is_secure):
        if is_secure:
            self.security_icon.setPixmap(load_icon("lock.svg", "#34a853").pixmap(16, 16))
            self.security_icon.setToolTip(tr("Secure connection (HTTPS)"))
        else:
            self.security_icon.setPixmap(load_icon("unlock.svg", "#ea4335").pixmap(16, 16))
            self.security_icon.setToolTip(tr("Insecure connection"))

    def set_bookmarked(self, is_bookmarked):
        self._is_bookmarked = is_bookmarked
        if is_bookmarked:
            self.bookmark_btn._icon_name = "bookmark.svg"
            self.bookmark_btn.setIcon(load_icon("bookmark.svg", "#f4b400"))
            self.bookmark_btn.setToolTip(tr("Remove Bookmark"))
        else:
            self.bookmark_btn._icon_name = "star.svg"
            self.bookmark_btn.setIcon(load_themed_icon("star.svg", self.dark_mode))
            self.bookmark_btn.setToolTip(f"{tr('Add Bookmark')} (Ctrl+D)")

    def set_navigation_state(self, can_back, can_forward):
        self.back_btn.setEnabled(can_back)
        self.forward_btn.setEnabled(can_forward)

    def update_suggestions(self, suggestions):
        self.address_bar.update_suggestions(suggestions)
