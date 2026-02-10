import logging

from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineSettings
from ..utils.constants import DEFAULT_USER_AGENT

log = logging.getLogger(__name__)


class BrowserEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._default_profile = None
        self._setup_default_profile()

    def _setup_default_profile(self):
        self._default_profile = QWebEngineProfile.defaultProfile()
        self._default_profile.setHttpUserAgent(DEFAULT_USER_AGENT)
        self._default_profile.setPersistentCookiesPolicy(
            QWebEngineProfile.ForcePersistentCookies
        )
        self._apply_settings(self._default_profile.settings())

    def _apply_settings(self, settings):
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, False)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, False)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadIconsForPage, True)
        settings.setAttribute(QWebEngineSettings.TouchIconsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FocusOnNavigationEnabled, True)
        settings.setAttribute(QWebEngineSettings.PrintElementBackgrounds, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, False)
        settings.setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, False)
        settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.ShowScrollBars, True)
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, True)
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, True)
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        settings.setDefaultTextEncoding("utf-8")

    @property
    def default_profile(self):
        return self._default_profile

    def create_private_profile(self, parent=None):
        profile = QWebEngineProfile(parent)
        profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        profile.setHttpUserAgent(DEFAULT_USER_AGENT)
        self._apply_settings(profile.settings())
        return profile

    def set_javascript_enabled(self, enabled: bool):
        self._default_profile.settings().setAttribute(
            QWebEngineSettings.JavascriptEnabled, enabled
        )

    def set_plugins_enabled(self, enabled: bool):
        self._default_profile.settings().setAttribute(
            QWebEngineSettings.PluginsEnabled, enabled
        )

    def set_images_enabled(self, enabled: bool):
        self._default_profile.settings().setAttribute(
            QWebEngineSettings.AutoLoadImages, enabled
        )

    def set_user_agent(self, user_agent: str):
        self._default_profile.setHttpUserAgent(user_agent)

    def clear_cache(self):
        self._default_profile.clearHttpCache()

    def clear_cookies(self):
        self._default_profile.cookieStore().deleteAllCookies()

    def clear_all_data(self):
        self.clear_cache()
        self.clear_cookies()
        self._default_profile.clearAllVisitedLinks()

    def get_cookie_store(self):
        return self._default_profile.cookieStore()

    def set_download_path(self, path: str):
        self._default_profile.setDownloadPath(path)

    def set_spell_check_enabled(self, enabled: bool, languages=None):
        self._default_profile.setSpellCheckEnabled(enabled)
        if languages:
            self._default_profile.setSpellCheckLanguages(languages)
