import logging

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QFrame, QLineEdit,
                             QStackedWidget, QToolButton)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont
from ..utils.constants import LIGHT_THEME, DARK_THEME
from ..utils.helpers import load_icon, load_themed_icon
from ..utils.i18n import _ as tr

log = logging.getLogger(__name__)


class SidebarNavButton(QToolButton):
    def __init__(self, icon_name, tooltip="", parent=None, dark_mode=False):
        super().__init__(parent)
        self._icon_name = icon_name
        self.setIcon(load_themed_icon(icon_name, dark_mode))
        self.setIconSize(QSize(18, 18))
        self.setToolTip(tooltip)
        self.setCheckable(True)
        self.setFixedSize(36, 36)
        self.setCursor(Qt.PointingHandCursor)

    def update_theme(self, dark_mode):
        self.setIcon(load_themed_icon(self._icon_name, dark_mode))


class BookmarkItemWidget(QFrame):
    clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(str)

    def __init__(self, bookmark, dark_mode=False, parent=None):
        super().__init__(parent)
        self.bookmark = bookmark
        self.dark_mode = dark_mode
        self.setObjectName("sidebarCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        icon_label = QLabel()
        icon_label.setPixmap(load_themed_icon("bookmark.svg", self.dark_mode).pixmap(14, 14))
        icon_label.setFixedSize(18, 18)
        layout.addWidget(icon_label)

        title_label = QLabel(self.bookmark.title[:35])
        title_label.setToolTip(self.bookmark.url)
        title_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(title_label, 1)

        del_btn = QToolButton()
        del_btn.setIcon(load_themed_icon("x.svg", self.dark_mode))
        del_btn.setIconSize(QSize(12, 12))
        del_btn.setFixedSize(20, 20)
        del_btn.setObjectName("deleteBtn")
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(self.bookmark.id))
        layout.addWidget(del_btn)

        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.bookmark.url)


class HistoryItemWidget(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, entry, dark_mode=False, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.dark_mode = dark_mode
        self.setObjectName("sidebarCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(2)

        top = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(load_themed_icon("clock.svg", self.dark_mode).pixmap(12, 12))
        icon_label.setFixedSize(16, 16)
        top.addWidget(icon_label)

        title_label = QLabel(self.entry.title[:40])
        title_label.setFont(QFont("Segoe UI", 9))
        top.addWidget(title_label, 1)
        layout.addLayout(top)

        url_label = QLabel(self.entry.url[:50])
        url_label.setObjectName("mutedText")
        url_label.setFont(QFont("Segoe UI", 8))
        layout.addWidget(url_label)

        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.entry.url)


class DownloadItemWidget(QFrame):
    open_clicked = pyqtSignal(str)
    cancel_clicked = pyqtSignal(str)

    def __init__(self, download, dark_mode=False, parent=None):
        super().__init__(parent)
        self.download = download
        self.dark_mode = dark_mode
        self.setObjectName("sidebarCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        top = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(load_themed_icon("download.svg", self.dark_mode).pixmap(14, 14))
        icon_label.setFixedSize(18, 18)
        top.addWidget(icon_label)

        name_label = QLabel(self.download.filename[:30])
        name_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        top.addWidget(name_label, 1)
        layout.addLayout(top)

        status_label = QLabel(f"{self.download.progress}% - {self.download.size_text}")
        status_label.setObjectName("mutedText")
        status_label.setFont(QFont("Segoe UI", 8))
        layout.addWidget(status_label)

        btn_layout = QHBoxLayout()
        if self.download.status == 'completed':
            open_btn = QPushButton(tr("Open"))
            open_btn.setFixedHeight(24)
            open_btn.clicked.connect(lambda: self.open_clicked.emit(self.download.id))
            btn_layout.addWidget(open_btn)
        elif self.download.status == 'downloading':
            cancel_btn = QPushButton(tr("Cancel"))
            cancel_btn.setFixedHeight(24)
            cancel_btn.clicked.connect(lambda: self.cancel_clicked.emit(self.download.id))
            btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)


class Sidebar(QWidget):
    bookmark_clicked = pyqtSignal(str)
    history_clicked = pyqtSignal(str)
    download_open_clicked = pyqtSignal(str)
    download_cancel_clicked = pyqtSignal(str)

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self._current_panel = None
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        self.setFixedWidth(300)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(8, 8, 8, 4)
        nav_layout.setSpacing(4)

        self.bookmarks_btn = SidebarNavButton("bookmark.svg", tr("Bookmarks"), dark_mode=self.dark_mode)
        self.bookmarks_btn.clicked.connect(lambda: self.show_panel("bookmarks"))

        self.history_btn = SidebarNavButton("clock.svg", tr("History"), dark_mode=self.dark_mode)
        self.history_btn.clicked.connect(lambda: self.show_panel("history"))

        self.downloads_btn = SidebarNavButton("download.svg", tr("Downloads"), dark_mode=self.dark_mode)
        self.downloads_btn.clicked.connect(lambda: self.show_panel("downloads"))

        for btn in [self.bookmarks_btn, self.history_btn, self.downloads_btn]:
            nav_layout.addWidget(btn)
        nav_layout.addStretch()

        self.close_btn = QToolButton()
        self.close_btn.setIcon(load_themed_icon("x.svg", self.dark_mode))
        self.close_btn.setIconSize(QSize(16, 16))
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.clicked.connect(self.hide)
        self.close_btn.setObjectName("closeBtn")
        nav_layout.addWidget(self.close_btn)
        main_layout.addLayout(nav_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("Search..."))
        self.search_input.textChanged.connect(self._on_search)
        main_layout.addWidget(self.search_input)

        self.stack = QStackedWidget()

        self.bookmarks_panel = self._create_panel(tr("Bookmarks"))
        self.bookmarks_scroll = self.bookmarks_panel.findChild(QScrollArea)
        self.bookmarks_container = QWidget()
        self.bookmarks_layout = QVBoxLayout(self.bookmarks_container)
        self.bookmarks_layout.setAlignment(Qt.AlignTop)
        self.bookmarks_layout.setContentsMargins(8, 0, 8, 8)
        self.bookmarks_layout.setSpacing(4)
        self.bookmarks_scroll.setWidget(self.bookmarks_container)
        self.stack.addWidget(self.bookmarks_panel)

        self.history_panel, self.clear_history_btn = self._create_panel_with_action(tr("History"), tr("Clear"))
        self.history_scroll = self.history_panel.findChild(QScrollArea)
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setAlignment(Qt.AlignTop)
        self.history_layout.setContentsMargins(8, 0, 8, 8)
        self.history_layout.setSpacing(4)
        self.history_scroll.setWidget(self.history_container)
        self.stack.addWidget(self.history_panel)

        self.downloads_panel = self._create_panel(tr("Downloads"))
        self.downloads_scroll = self.downloads_panel.findChild(QScrollArea)
        self.downloads_container = QWidget()
        self.downloads_layout = QVBoxLayout(self.downloads_container)
        self.downloads_layout.setAlignment(Qt.AlignTop)
        self.downloads_layout.setContentsMargins(8, 0, 8, 8)
        self.downloads_layout.setSpacing(4)
        self.downloads_scroll.setWidget(self.downloads_container)
        self.stack.addWidget(self.downloads_panel)

        main_layout.addWidget(self.stack)
        self.show_panel("bookmarks")

    def _create_panel(self, title):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        header = QLabel(title)
        header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header.setContentsMargins(12, 8, 12, 8)
        layout.addWidget(header)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(scroll)
        return panel

    def _create_panel_with_action(self, title, action_text):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 8, 12, 8)
        header = QLabel(title)
        header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header_layout.addWidget(header)
        header_layout.addStretch()
        action_btn = QPushButton(action_text)
        action_btn.setFixedHeight(24)
        action_btn.setObjectName("actionBtn")
        header_layout.addWidget(action_btn)
        layout.addLayout(header_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(scroll)
        return panel, action_btn

    def _apply_style(self):
        theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        self.setStyleSheet(f"""
            Sidebar {{
                background-color: {theme['bg_secondary']};
                border-right: 1px solid {theme['border']};
            }}
            QLabel {{
                color: {theme['text_primary']};
            }}
            #mutedText {{
                color: {theme['text_muted']};
            }}
            QLineEdit {{
                background-color: {theme['bg_tertiary']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 8px 12px;
                margin: 4px 8px 8px 8px;
                font-size: 13px;
                color: {theme['text_primary']};
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}
            QLineEdit:focus {{
                border-color: {theme['accent']};
            }}
            #sidebarCard {{
                background-color: {theme['card']};
                border-radius: 8px;
                border: 1px solid {theme['border_light']};
            }}
            #sidebarCard:hover {{
                background-color: {theme['card_hover']};
            }}
            QPushButton, #actionBtn {{
                background-color: {theme['bg_tertiary']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                color: {theme['text_primary']};
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}
            QPushButton:hover, #actionBtn:hover {{
                background-color: {theme['accent']};
                color: white;
            }}
            QToolButton {{
                background: transparent;
                border: none;
                border-radius: 8px;
            }}
            QToolButton:hover {{
                background-color: {theme['bg_hover']};
            }}
            QToolButton:checked {{
                background-color: {theme['accent_light']};
            }}
            #deleteBtn {{
                border-radius: 4px;
            }}
            #deleteBtn:hover {{
                background-color: {theme['error']};
            }}
            #closeBtn:hover {{
                background-color: {theme['error']};
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
        """)

    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
        self._apply_style()
        for btn in [self.bookmarks_btn, self.history_btn, self.downloads_btn]:
            btn.update_theme(dark_mode)
        self.close_btn.setIcon(load_themed_icon("x.svg", dark_mode))

    def show_panel(self, panel_name):
        self._current_panel = panel_name
        self.bookmarks_btn.setChecked(panel_name == "bookmarks")
        self.history_btn.setChecked(panel_name == "history")
        self.downloads_btn.setChecked(panel_name == "downloads")
        if panel_name == "bookmarks":
            self.stack.setCurrentWidget(self.bookmarks_panel)
        elif panel_name == "history":
            self.stack.setCurrentWidget(self.history_panel)
        elif panel_name == "downloads":
            self.stack.setCurrentWidget(self.downloads_panel)
        self.show()

    def _on_search(self, text):
        if not text:
            self._show_all_items()
            return
        text_lower = text.lower()
        if self._current_panel == "bookmarks":
            self._filter_items(self.bookmarks_layout, text_lower)
        elif self._current_panel == "history":
            self._filter_items(self.history_layout, text_lower)
        elif self._current_panel == "downloads":
            self._filter_items(self.downloads_layout, text_lower)

    def _filter_items(self, layout, text):
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget:
                tooltip = widget.toolTip() or ""
                labels = widget.findChildren(QLabel)
                visible = any(text in lbl.text().lower() for lbl in labels) or text in tooltip.lower()
                widget.setVisible(visible)

    def _show_all_items(self):
        for layout in (self.bookmarks_layout, self.history_layout, self.downloads_layout):
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if widget:
                    widget.setVisible(True)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def update_bookmarks(self, bookmarks):
        self._clear_layout(self.bookmarks_layout)
        for bookmark in bookmarks:
            item = BookmarkItemWidget(bookmark, self.dark_mode)
            item.clicked.connect(self.bookmark_clicked.emit)
            self.bookmarks_layout.addWidget(item)
        if not bookmarks:
            empty = QLabel(tr("No bookmarks yet"))
            empty.setAlignment(Qt.AlignCenter)
            empty.setObjectName("mutedText")
            empty.setContentsMargins(0, 20, 0, 20)
            self.bookmarks_layout.addWidget(empty)

    def update_history(self, entries):
        self._clear_layout(self.history_layout)
        for entry in entries[:50]:
            item = HistoryItemWidget(entry, self.dark_mode)
            item.clicked.connect(self.history_clicked.emit)
            self.history_layout.addWidget(item)
        if not entries:
            empty = QLabel(tr("No history yet"))
            empty.setAlignment(Qt.AlignCenter)
            empty.setObjectName("mutedText")
            empty.setContentsMargins(0, 20, 0, 20)
            self.history_layout.addWidget(empty)

    def update_downloads(self, downloads):
        self._clear_layout(self.downloads_layout)
        for download in downloads:
            item = DownloadItemWidget(download, self.dark_mode)
            item.open_clicked.connect(self.download_open_clicked.emit)
            item.cancel_clicked.connect(self.download_cancel_clicked.emit)
            self.downloads_layout.addWidget(item)
        if not downloads:
            empty = QLabel(tr("No downloads yet"))
            empty.setAlignment(Qt.AlignCenter)
            empty.setObjectName("mutedText")
            empty.setContentsMargins(0, 20, 0, 20)
            self.downloads_layout.addWidget(empty)
