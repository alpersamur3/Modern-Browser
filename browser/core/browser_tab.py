"""
Browser Tab - Individual tab management
"""

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtCore import QUrl, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from datetime import datetime
from ..utils.constants import ZOOM_DEFAULT, ZOOM_MIN, ZOOM_MAX, ZOOM_STEP


class BrowserPage(QWebEnginePage):
    """Custom web page for additional features"""
    
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self._parent_tab = parent
    
    def createWindow(self, window_type):
        """Handle new window/tab requests"""
        if self._parent_tab and hasattr(self._parent_tab, 'new_tab_requested'):
            return self._parent_tab.request_new_tab()
        return super().createWindow(window_type)
    
    def certificateError(self, error):
        """
        Handle SSL certificate errors securely.
        Always reject invalid certificates to protect users from
        man-in-the-middle attacks and phishing attempts.
        
        Future enhancement: Could show a warning dialog letting 
        users make an informed decision for self-signed certificates.
        """
        # Security: Never accept invalid certificates automatically
        # This protects users from MITM attacks
        return False


class BrowserTab(QWebEngineView):
    """
    Enhanced browser tab with modern features
    """
    
    # Signals
    new_tab_requested = pyqtSignal(object)  # QUrl
    favicon_changed = pyqtSignal(object)  # QIcon
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
        
        # Setup profile
        if private:
            self._profile = QWebEngineProfile(self)
            self._profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
            self._profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        else:
            self._profile = profile or QWebEngineProfile.defaultProfile()
        
        # Setup custom page
        self._page = BrowserPage(self._profile, self)
        self.setPage(self._page)
        
        # Connect signals
        self.loadStarted.connect(self._on_load_started)
        self.loadProgress.connect(self._on_load_progress)
        self.loadFinished.connect(self._on_load_finished)
        self.iconChanged.connect(self._on_icon_changed)
        self.urlChanged.connect(self._on_url_changed)
        
        # Page audio signal
        self.page().recentlyAudibleChanged.connect(self._on_audio_changed)
    
    def request_new_tab(self):
        """Request a new tab from parent window"""
        if self.browser_window:
            return self.browser_window.add_new_tab(private=self.private)
        return None
    
    # Loading events
    def _on_load_started(self):
        self._loading = True
    
    def _on_load_progress(self, progress):
        self.loading_progress.emit(progress)
    
    def _on_load_finished(self, success):
        self._loading = False
        if success:
            self._add_to_local_history()
            # Check security
            url = self.url()
            is_secure = url.scheme() == 'https'
            self.security_changed.emit(is_secure)
    
    def _on_icon_changed(self, icon):
        self.favicon_changed.emit(icon)
    
    def _on_url_changed(self, url):
        pass  # Handled by main window
    
    def _on_audio_changed(self, audible):
        self._is_playing_audio = audible
        self.audio_changed.emit(audible)
    
    # History management
    def _add_to_local_history(self):
        """Add current page to local tab history"""
        if self.private:
            return
        
        entry = {
            'url': self.url().toString(),
            'title': self.page().title() or "Untitled",
            'timestamp': datetime.now().isoformat()
        }
        
        # Remove forward history if navigating from middle
        if self._current_history_index < len(self._history_entries) - 1:
            self._history_entries = self._history_entries[:self._current_history_index + 1]
        
        self._history_entries.append(entry)
        self._current_history_index = len(self._history_entries) - 1
    
    # Zoom methods
    def get_zoom(self):
        """Get current zoom percentage"""
        return int(self.zoomFactor() * 100)
    
    def set_zoom(self, percentage):
        """Set zoom percentage"""
        percentage = max(ZOOM_MIN, min(ZOOM_MAX, percentage))
        self._zoom_factor = percentage
        self.setZoomFactor(percentage / 100.0)
        return percentage
    
    def zoom_in(self):
        """Zoom in by step"""
        return self.set_zoom(self.get_zoom() + ZOOM_STEP)
    
    def zoom_out(self):
        """Zoom out by step"""
        return self.set_zoom(self.get_zoom() - ZOOM_STEP)
    
    def zoom_reset(self):
        """Reset zoom to default"""
        return self.set_zoom(ZOOM_DEFAULT)
    
    # Mute methods
    @property
    def is_muted(self):
        return self._is_muted
    
    def set_muted(self, muted):
        """Set tab mute state"""
        self._is_muted = muted
        self.page().setAudioMuted(muted)
    
    def toggle_mute(self):
        """Toggle mute state"""
        self.set_muted(not self._is_muted)
        return self._is_muted
    
    # Pin methods
    @property
    def is_pinned(self):
        return self._is_pinned
    
    def set_pinned(self, pinned):
        """Set tab pin state"""
        self._is_pinned = pinned
    
    def toggle_pin(self):
        """Toggle pin state"""
        self._is_pinned = not self._is_pinned
        return self._is_pinned
    
    # State properties
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
    
    # Page operations
    def reload_hard(self):
        """Hard reload ignoring cache"""
        self.page().triggerAction(QWebEnginePage.ReloadAndBypassCache)
    
    def stop_loading(self):
        """Stop page loading"""
        self.stop()
    
    def get_page_source(self, callback):
        """Get page HTML source"""
        self.page().toHtml(callback)
    
    def get_page_text(self, callback):
        """Get page plain text"""
        self.page().toPlainText(callback)
    
    def run_javascript(self, script, callback=None):
        """Run JavaScript on the page"""
        if callback:
            self.page().runJavaScript(script, callback)
        else:
            self.page().runJavaScript(script)
    
    def find_text(self, text, flags=0):
        """Find text on page"""
        self.page().findText(text, QWebEnginePage.FindFlags(flags))
    
    def clear_find(self):
        """Clear find highlighting"""
        self.page().findText("")
    
    def print_page(self, printer=None):
        """Print the page"""
        if printer:
            self.page().print(printer, lambda ok: None)
    
    def save_page(self, path, format_type=None):
        """Save page to file"""
        from PyQt5.QtWebEngineWidgets import QWebEngineDownloadItem
        if format_type is None:
            format_type = QWebEngineDownloadItem.CompleteHtmlSaveFormat
        self.page().save(path, format_type)
    
    # Screenshot
    def take_screenshot(self, callback):
        """Take screenshot of visible area"""
        # Use grab() to capture the view
        pixmap = self.grab()
        callback(pixmap)
    
    def take_full_screenshot(self, callback):
        """Take screenshot of full page"""
        # This requires running JS to get full page size
        script = """
        (function() {
            return {
                width: Math.max(document.body.scrollWidth, document.documentElement.scrollWidth),
                height: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
            };
        })();
        """
        self.page().runJavaScript(script, lambda size: self._capture_full_page(size, callback))
    
    def _capture_full_page(self, size, callback):
        """Internal method to capture full page"""
        # For now, just capture visible area
        # Full page screenshot requires more complex implementation
        callback(self.grab())
    
    # Inject custom CSS/JS
    def inject_css(self, css):
        """Inject CSS into page"""
        script = f"""
        (function() {{
            var style = document.createElement('style');
            style.type = 'text/css';
            style.innerHTML = `{css}`;
            document.head.appendChild(style);
        }})();
        """
        self.page().runJavaScript(script)
    
    def inject_dark_mode(self):
        """Inject dark mode CSS"""
        dark_css = """
        html {
            filter: invert(90%) hue-rotate(180deg) !important;
            background-color: #111 !important;
        }
        img, video, picture, canvas, [style*="background-image"] {
            filter: invert(100%) hue-rotate(180deg) !important;
        }
        """
        self.inject_css(dark_css)
    
    # Title
    def get_title(self):
        """Get page title"""
        title = self.page().title()
        if self.private and not title:
            return "Gizli Sekme"
        return title or "Yeni Sekme"
    
    # Cleanup
    def cleanup(self):
        """Cleanup tab resources"""
        self.stop()
        self.setUrl(QUrl("about:blank"))
