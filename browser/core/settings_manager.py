"""
Settings Manager for Modern Browser
"""

import json
import os
from PyQt5.QtCore import QSettings, QStandardPaths
from ..utils.constants import (
    APP_NAME, APP_ORGANIZATION, DEFAULT_HOME_URL, 
    DEFAULT_SEARCH_ENGINE, DEFAULT_LANGUAGE, ZOOM_DEFAULT
)


class SettingsManager:
    """Manages all browser settings with persistent storage"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.settings = QSettings(APP_ORGANIZATION, APP_NAME)
        self._initialized = True
        self._init_defaults()
    
    def _init_defaults(self):
        """Initialize default settings if not present"""
        defaults = {
            # General
            "general/homepage": DEFAULT_HOME_URL,
            "general/search_engine": DEFAULT_SEARCH_ENGINE,
            "general/language": DEFAULT_LANGUAGE,
            "general/startup": "homepage",  # homepage, continue, blank
            "general/new_tab_page": "homepage",
            "general/restore_session": False,
            
            # Appearance
            "appearance/dark_mode": False,
            "appearance/theme": "default",
            "appearance/font_family": "Segoe UI",
            "appearance/font_size": 14,
            "appearance/show_bookmarks_bar": True,
            "appearance/show_status_bar": True,
            "appearance/compact_mode": False,
            "appearance/animation_enabled": True,
            
            # Privacy
            "privacy/do_not_track": True,
            "privacy/block_third_party_cookies": False,
            "privacy/clear_on_exit": False,
            "privacy/save_passwords": True,
            "privacy/autofill": True,
            
            # Security
            "security/ad_blocker": True,
            "security/phishing_protection": True,
            "security/https_only": False,
            "security/javascript_enabled": True,
            
            # Downloads
            "downloads/path": QStandardPaths.writableLocation(QStandardPaths.DownloadLocation),
            "downloads/ask_location": False,
            "downloads/auto_open": False,
            
            # Tabs
            "tabs/close_button_on_tabs": True,
            "tabs/open_adjacent": True,
            "tabs/switch_to_new": True,
            "tabs/warn_on_close_multiple": True,
            
            # Zoom
            "zoom/default": ZOOM_DEFAULT,
            "zoom/per_site": {},
            
            # Advanced
            "advanced/hardware_acceleration": True,
            "advanced/smooth_scrolling": True,
            "advanced/prefetch": True,
            "advanced/developer_mode": False
        }
        
        for key, value in defaults.items():
            if self.settings.value(key) is None:
                if isinstance(value, dict):
                    self.settings.setValue(key, json.dumps(value))
                else:
                    self.settings.setValue(key, value)
    
    # General Settings
    @property
    def homepage(self):
        return self.settings.value("general/homepage", DEFAULT_HOME_URL)
    
    @homepage.setter
    def homepage(self, value):
        self.settings.setValue("general/homepage", value)
    
    @property
    def search_engine(self):
        return self.settings.value("general/search_engine", DEFAULT_SEARCH_ENGINE)
    
    @search_engine.setter
    def search_engine(self, value):
        self.settings.setValue("general/search_engine", value)
    
    @property
    def language(self):
        return self.settings.value("general/language", DEFAULT_LANGUAGE)
    
    @language.setter
    def language(self, value):
        self.settings.setValue("general/language", value)
    
    @property
    def startup_behavior(self):
        return self.settings.value("general/startup", "homepage")
    
    @startup_behavior.setter
    def startup_behavior(self, value):
        self.settings.setValue("general/startup", value)
    
    @property
    def restore_session(self):
        return self.settings.value("general/restore_session", False, type=bool)
    
    @restore_session.setter
    def restore_session(self, value):
        self.settings.setValue("general/restore_session", value)
    
    # Appearance Settings
    @property
    def dark_mode(self):
        return self.settings.value("appearance/dark_mode", False, type=bool)
    
    @dark_mode.setter
    def dark_mode(self, value):
        self.settings.setValue("appearance/dark_mode", value)
    
    @property
    def theme(self):
        return self.settings.value("appearance/theme", "default")
    
    @theme.setter
    def theme(self, value):
        self.settings.setValue("appearance/theme", value)
    
    @property
    def show_bookmarks_bar(self):
        return self.settings.value("appearance/show_bookmarks_bar", True, type=bool)
    
    @show_bookmarks_bar.setter
    def show_bookmarks_bar(self, value):
        self.settings.setValue("appearance/show_bookmarks_bar", value)
    
    @property
    def show_status_bar(self):
        return self.settings.value("appearance/show_status_bar", True, type=bool)
    
    @show_status_bar.setter
    def show_status_bar(self, value):
        self.settings.setValue("appearance/show_status_bar", value)
    
    @property
    def animation_enabled(self):
        return self.settings.value("appearance/animation_enabled", True, type=bool)
    
    @animation_enabled.setter
    def animation_enabled(self, value):
        self.settings.setValue("appearance/animation_enabled", value)
    
    # Privacy Settings
    @property
    def do_not_track(self):
        return self.settings.value("privacy/do_not_track", True, type=bool)
    
    @do_not_track.setter
    def do_not_track(self, value):
        self.settings.setValue("privacy/do_not_track", value)
    
    @property
    def save_passwords(self):
        return self.settings.value("privacy/save_passwords", True, type=bool)
    
    @save_passwords.setter
    def save_passwords(self, value):
        self.settings.setValue("privacy/save_passwords", value)
    
    @property
    def clear_on_exit(self):
        return self.settings.value("privacy/clear_on_exit", False, type=bool)
    
    @clear_on_exit.setter
    def clear_on_exit(self, value):
        self.settings.setValue("privacy/clear_on_exit", value)
    
    # Security Settings
    @property
    def ad_blocker_enabled(self):
        return self.settings.value("security/ad_blocker", True, type=bool)
    
    @ad_blocker_enabled.setter
    def ad_blocker_enabled(self, value):
        self.settings.setValue("security/ad_blocker", value)
    
    @property
    def javascript_enabled(self):
        return self.settings.value("security/javascript_enabled", True, type=bool)
    
    @javascript_enabled.setter
    def javascript_enabled(self, value):
        self.settings.setValue("security/javascript_enabled", value)
    
    @property
    def https_only(self):
        return self.settings.value("security/https_only", False, type=bool)
    
    @https_only.setter
    def https_only(self, value):
        self.settings.setValue("security/https_only", value)
    
    # Download Settings
    @property
    def download_path(self):
        default = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        return self.settings.value("downloads/path", default)
    
    @download_path.setter
    def download_path(self, value):
        self.settings.setValue("downloads/path", value)
    
    @property
    def ask_download_location(self):
        return self.settings.value("downloads/ask_location", False, type=bool)
    
    @ask_download_location.setter
    def ask_download_location(self, value):
        self.settings.setValue("downloads/ask_location", value)
    
    # Zoom Settings
    @property
    def default_zoom(self):
        return self.settings.value("zoom/default", ZOOM_DEFAULT, type=int)
    
    @default_zoom.setter
    def default_zoom(self, value):
        self.settings.setValue("zoom/default", value)
    
    def get_site_zoom(self, domain):
        """Get zoom level for specific site"""
        zoom_data = json.loads(self.settings.value("zoom/per_site", "{}"))
        return zoom_data.get(domain, self.default_zoom)
    
    def set_site_zoom(self, domain, zoom):
        """Set zoom level for specific site"""
        zoom_data = json.loads(self.settings.value("zoom/per_site", "{}"))
        zoom_data[domain] = zoom
        self.settings.setValue("zoom/per_site", json.dumps(zoom_data))
    
    # Tab Settings
    @property
    def close_button_on_tabs(self):
        return self.settings.value("tabs/close_button_on_tabs", True, type=bool)
    
    @close_button_on_tabs.setter
    def close_button_on_tabs(self, value):
        self.settings.setValue("tabs/close_button_on_tabs", value)
    
    @property
    def switch_to_new_tab(self):
        return self.settings.value("tabs/switch_to_new", True, type=bool)
    
    @switch_to_new_tab.setter
    def switch_to_new_tab(self, value):
        self.settings.setValue("tabs/switch_to_new", value)
    
    @property
    def warn_on_close_multiple(self):
        return self.settings.value("tabs/warn_on_close_multiple", True, type=bool)
    
    @warn_on_close_multiple.setter
    def warn_on_close_multiple(self, value):
        self.settings.setValue("tabs/warn_on_close_multiple", value)
    
    # Advanced Settings
    @property
    def hardware_acceleration(self):
        return self.settings.value("advanced/hardware_acceleration", True, type=bool)
    
    @hardware_acceleration.setter
    def hardware_acceleration(self, value):
        self.settings.setValue("advanced/hardware_acceleration", value)
    
    @property
    def smooth_scrolling(self):
        return self.settings.value("advanced/smooth_scrolling", True, type=bool)
    
    @smooth_scrolling.setter
    def smooth_scrolling(self, value):
        self.settings.setValue("advanced/smooth_scrolling", value)
    
    @property
    def developer_mode(self):
        return self.settings.value("advanced/developer_mode", False, type=bool)
    
    @developer_mode.setter
    def developer_mode(self, value):
        self.settings.setValue("advanced/developer_mode", value)
    
    # Utility Methods
    def get(self, key, default=None):
        """Get any setting by key"""
        value = self.settings.value(key, default)
        if value is None:
            return default
        return value
    
    def set(self, key, value):
        """Set any setting by key"""
        self.settings.setValue(key, value)
    
    def sync(self):
        """Force sync settings to storage"""
        self.settings.sync()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings.clear()
        self._init_defaults()
    
    def export_settings(self, filepath):
        """Export settings to JSON file"""
        all_settings = {}
        for key in self.settings.allKeys():
            all_settings[key] = self.settings.value(key)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_settings, f, indent=2, ensure_ascii=False)
    
    def import_settings(self, filepath):
        """Import settings from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            all_settings = json.load(f)
        
        for key, value in all_settings.items():
            self.settings.setValue(key, value)
