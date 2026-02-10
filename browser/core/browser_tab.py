import logging
from datetime import datetime

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtCore import QUrl, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from ..utils.constants import ZOOM_DEFAULT, ZOOM_MIN, ZOOM_MAX, ZOOM_STEP

log = logging.getLogger(__name__)


class BrowserPage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self._parent_tab = parent

    def createWindow(self, window_type):
        if self._parent_tab and hasattr(self._parent_tab, 'request_new_tab'):
            new_tab = self._parent_tab.request_new_tab()
            if new_tab:
                return new_tab.page()
        return super().createWindow(window_type)

    def certificateError(self, error):
        return False


class BrowserTab(QWebEngineView):
    new_tab_requested = pyqtSignal(object)
    favicon_changed = pyqtSignal(object)
    loading_progress = pyqtSignal(int)
    security_changed = pyqtSignal(bool)
    audio_changed = pyqtSignal(bool)

    def __init__(self, parent=None, private=False, profile=None):
        super().__init__(parent)
        self.browser_window = parent
        self.private = private
        self._zoom_factor = ZOOM_DEFAULT
        self._is_muted = False
        self._is_pinned = False
        self._loading = False
        self._is_playing_audio = False
        self._history_entries = []
        self._current_history_index = -1

        if private and profile:
            self._profile = profile
        elif private:
            from .browser_engine import BrowserEngine
            engine = BrowserEngine()
            self._profile = engine.create_private_profile(self)
        else:
            self._profile = profile or QWebEngineProfile.defaultProfile()

        self._page = BrowserPage(self._profile, self)
        self.setPage(self._page)

        self.loadStarted.connect(self._on_load_started)
        self.loadProgress.connect(self._on_load_progress)
        self.loadFinished.connect(self._on_load_finished)
        self.iconChanged.connect(self._on_icon_changed)
        self.urlChanged.connect(self._on_url_changed)
        self.page().recentlyAudibleChanged.connect(self._on_audio_changed)

    def request_new_tab(self):
        if self.browser_window:
            return self.browser_window.add_new_tab(private=self.private)
        return None

    def _on_load_started(self):
        self._loading = True

    def _on_load_progress(self, progress):
        self.loading_progress.emit(progress)

    def _on_load_finished(self, success):
        self._loading = False
        if success:
            self._add_to_local_history()
            is_secure = self.url().scheme() == 'https'
            self.security_changed.emit(is_secure)

    def _on_icon_changed(self, icon):
        self.favicon_changed.emit(icon)

    def _on_url_changed(self, url):
        pass

    def _on_audio_changed(self, audible):
        self._is_playing_audio = audible
        self.audio_changed.emit(audible)

    def _add_to_local_history(self):
        if self.private:
            return
        entry = {
            'url': self.url().toString(),
            'title': self.page().title() or "Untitled",
            'timestamp': datetime.now().isoformat()
        }
        if self._current_history_index < len(self._history_entries) - 1:
            self._history_entries = self._history_entries[:self._current_history_index + 1]
        self._history_entries.append(entry)
        self._current_history_index = len(self._history_entries) - 1

    def get_zoom(self):
        return int(self.zoomFactor() * 100)

    def set_zoom(self, percentage):
        percentage = max(ZOOM_MIN, min(ZOOM_MAX, percentage))
        self._zoom_factor = percentage
        self.setZoomFactor(percentage / 100.0)
        return percentage

    def zoom_in(self):
        return self.set_zoom(self.get_zoom() + ZOOM_STEP)

    def zoom_out(self):
        return self.set_zoom(self.get_zoom() - ZOOM_STEP)

    def zoom_reset(self):
        return self.set_zoom(ZOOM_DEFAULT)

    @property
    def is_muted(self):
        return self._is_muted

    def set_muted(self, muted):
        self._is_muted = muted
        self.page().setAudioMuted(muted)

    def toggle_mute(self):
        self.set_muted(not self._is_muted)
        return self._is_muted

    @property
    def is_pinned(self):
        return self._is_pinned

    def set_pinned(self, pinned):
        self._is_pinned = pinned

    def toggle_pin(self):
        self._is_pinned = not self._is_pinned
        return self._is_pinned

    @property
    def is_loading(self):
        return self._loading

    @property
    def is_playing_audio(self):
        return self._is_playing_audio

    @property
    def is_private(self):
        return self.private

    @property
    def is_secure(self):
        return self.url().scheme() == 'https'

    def reload_hard(self):
        self.page().triggerAction(QWebEnginePage.ReloadAndBypassCache)

    def stop_loading(self):
        self.stop()

    def get_page_source(self, callback):
        self.page().toHtml(callback)

    def get_page_text(self, callback):
        self.page().toPlainText(callback)

    def run_javascript(self, script, callback=None):
        if callback:
            self.page().runJavaScript(script, callback)
        else:
            self.page().runJavaScript(script)

    def find_text(self, text, flags=0):
        self.page().findText(text, QWebEnginePage.FindFlags(flags))

    def clear_find(self):
        self.page().findText("")

    def print_page(self, printer=None):
        if printer:
            self.page().print(printer, lambda ok: None)

    def save_page(self, path, format_type=None):
        from PyQt5.QtWebEngineWidgets import QWebEngineDownloadItem
        if format_type is None:
            format_type = QWebEngineDownloadItem.CompleteHtmlSaveFormat
        self.page().save(path, format_type)

    def take_screenshot(self, callback):
        pixmap = self.grab()
        callback(pixmap)

    def take_full_screenshot(self, callback):
        script = '''
        (function() {
            return {
                width: Math.max(document.body.scrollWidth, document.documentElement.scrollWidth),
                height: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
            };
        })();
        '''
        self.page().runJavaScript(script, lambda size: callback(self.grab()))

    def inject_css(self, css):
        safe_css = css.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
        script = '''
        (function() {
            if (!document || !document.head) return;
            var style = document.createElement('style');
            style.type = 'text/css';
            style.setAttribute('data-injected', 'true');
            style.innerHTML = `''' + safe_css + '''`;
            document.head.appendChild(style);
        })();
        '''
        self.page().runJavaScript(script)

    def inject_dark_mode(self):
        dark_css = '''
        html {
            filter: invert(90%) hue-rotate(180deg) !important;
            background-color: #111 !important;
        }
        img, video, picture, canvas, [style*="background-image"] {
            filter: invert(100%) hue-rotate(180deg) !important;
        }
        '''
        url = self.url().toString()
        if url.startswith('about:') or url.startswith('data:') or not url:
            return
        self.inject_css(dark_css)

    def remove_injected_css(self):
        script = '''
        (function() {
            if (!document) return;
            document.querySelectorAll('style[data-injected]').forEach(function(s) { s.remove(); });
        })();
        '''
        self.page().runJavaScript(script)

    def get_title(self):
        title = self.page().title()
        if self.private and not title:
            return "Gizli Sekme"
        return title or "Yeni Sekme"

    def open_dev_tools(self):
        if self.browser_window:
            dev_tab = self.browser_window.add_new_tab()
            if dev_tab:
                self.page().setDevToolsPage(dev_tab.page())
                return dev_tab
        return None

    def cleanup(self):
        self.stop()
        self.setUrl(QUrl("about:blank"))
