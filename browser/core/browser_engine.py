"""
Browser Engine - Core engine management
"""

from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineSettings
from PyQt5.QtCore import QUrl
from ..utils.constants import DEFAULT_USER_AGENT


class BrowserEngine:
    """
    Manages the browser engine settings and profiles
    """
    
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
        self._private_profile = None
        self._setup_default_profile()
    
    def _setup_default_profile(self):
        """Setup the default browser profile"""
        self._default_profile = QWebEngineProfile.defaultProfile()
        
        # Set user agent
        self._default_profile.setHttpUserAgent(DEFAULT_USER_AGENT)
        
        # Enable persistent cookies
        self._default_profile.setPersistentCookiesPolicy(
            QWebEngineProfile.ForcePersistentCookies
        )
        
        # Setup settings
        self._apply_settings(self._default_profile.settings())
    
    def _apply_settings(self, settings):
        """Apply common settings to a profile"""
        # Enable features
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
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
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, False)
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        
        # Set default encoding
        settings.setDefaultTextEncoding("utf-8")
    
    @property
    def default_profile(self):
        """Get the default browser profile"""
        return self._default_profile
    
    def create_private_profile(self):
        """Create a new private (incognito) profile"""
        profile = QWebEngineProfile()
        
        # Private mode settings
        profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        profile.setHttpUserAgent(DEFAULT_USER_AGENT)
        
        # Apply common settings
        self._apply_settings(profile.settings())
        
        return profile
    
    def set_javascript_enabled(self, enabled):
        """Enable or disable JavaScript"""
        self._default_profile.settings().setAttribute(
            QWebEngineSettings.JavascriptEnabled, enabled
        )
    
    def set_plugins_enabled(self, enabled):
        """Enable or disable plugins"""
        self._default_profile.settings().setAttribute(
            QWebEngineSettings.PluginsEnabled, enabled
        )
    
    def set_images_enabled(self, enabled):
        """Enable or disable images"""
        self._default_profile.settings().setAttribute(
            QWebEngineSettings.AutoLoadImages, enabled
        )
    
    def set_user_agent(self, user_agent):
        """Set custom user agent"""
        self._default_profile.setHttpUserAgent(user_agent)
    
    def clear_cache(self):
        """Clear the HTTP cache"""
        self._default_profile.clearHttpCache()
    
    def clear_cookies(self):
        """Clear all cookies"""
        self._default_profile.cookieStore().deleteAllCookies()
    
    def clear_all_data(self):
        """Clear all browsing data"""
        self.clear_cache()
        self.clear_cookies()
        self._default_profile.clearAllVisitedLinks()
    
    def get_cookie_store(self):
        """Get the cookie store for advanced cookie management"""
        return self._default_profile.cookieStore()
    
    def set_download_path(self, path):
        """Set default download path"""
        self._default_profile.setDownloadPath(path)
    
    def set_spell_check_enabled(self, enabled, languages=None):
        """Enable spell checking"""
        self._default_profile.setSpellCheckEnabled(enabled)
        if languages:
            self._default_profile.setSpellCheckLanguages(languages)
    
    def set_cache_path(self, path):
        """Set cache storage path"""
        self._default_profile.setCachePath(path)
    
    def set_persistent_storage_path(self, path):
        """Set persistent storage path"""
        self._default_profile.setPersistentStoragePath(path)
    
    def get_settings(self):
        """Get current engine settings"""
        settings = self._default_profile.settings()
        return {
            'javascript': settings.testAttribute(QWebEngineSettings.JavascriptEnabled),
            'plugins': settings.testAttribute(QWebEngineSettings.PluginsEnabled),
            'images': settings.testAttribute(QWebEngineSettings.AutoLoadImages),
            'local_storage': settings.testAttribute(QWebEngineSettings.LocalStorageEnabled),
            'webgl': settings.testAttribute(QWebEngineSettings.WebGLEnabled),
            'fullscreen': settings.testAttribute(QWebEngineSettings.FullScreenSupportEnabled)
        }
