"""
Search Manager for Modern Browser
"""

from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from ..utils.constants import (
    APP_NAME, APP_ORGANIZATION, SEARCH_ENGINES, DEFAULT_SEARCH_ENGINE
)
from ..utils.helpers import normalize_url, url_encode


class SearchManager(QObject):
    """Manages search engine selection and search queries"""
    
    # Signals
    search_engine_changed = pyqtSignal(str)
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        super().__init__()
        self._initialized = True
        self.settings = QSettings(APP_ORGANIZATION, APP_NAME)
        self._custom_engines = {}
        self._load_custom_engines()
    
    def _load_custom_engines(self):
        """Load custom search engines from settings"""
        import json
        engines_json = self.settings.value("search/custom_engines", "{}")
        try:
            self._custom_engines = json.loads(engines_json)
        except:
            self._custom_engines = {}
    
    def _save_custom_engines(self):
        """Save custom search engines to settings"""
        import json
        self.settings.setValue("search/custom_engines", json.dumps(self._custom_engines))
    
    @property
    def current_engine(self):
        """Get current search engine name"""
        return self.settings.value("general/search_engine", DEFAULT_SEARCH_ENGINE)
    
    @current_engine.setter
    def current_engine(self, name):
        """Set current search engine"""
        self.settings.setValue("general/search_engine", name)
        self.search_engine_changed.emit(name)
    
    def get_all_engines(self):
        """Get all available search engines"""
        engines = dict(SEARCH_ENGINES)
        engines.update(self._custom_engines)
        return engines
    
    def get_engine_url(self, name=None):
        """Get search URL template for an engine"""
        if name is None:
            name = self.current_engine
        
        engines = self.get_all_engines()
        return engines.get(name, SEARCH_ENGINES[DEFAULT_SEARCH_ENGINE])
    
    def get_search_url(self, query, engine=None):
        """Get the full search URL for a query"""
        url_template = self.get_engine_url(engine)
        return url_template.format(url_encode(query))
    
    def process_input(self, text):
        """
        Process address bar input.
        Returns (url, is_search) tuple.
        """
        text = text.strip()
        
        if not text:
            return None, False
        
        # Check for special commands
        if text.startswith('!'):
            return self._process_bang_command(text)
        
        # Try to normalize as URL
        url = normalize_url(text)
        
        if url:
            return url, False
        else:
            # It's a search query
            return self.get_search_url(text), True
    
    def _process_bang_command(self, text):
        """Process DuckDuckGo-style bang commands"""
        parts = text.split(' ', 1)
        bang = parts[0].lower()
        query = parts[1] if len(parts) > 1 else ''
        
        bang_map = {
            '!g': 'Google',
            '!d': 'DuckDuckGo',
            '!b': 'Bing',
            '!y': 'Yahoo',
            '!ya': 'Yandex',
            '!e': 'Ecosia',
            '!br': 'Brave',
            # Add more as needed
        }
        
        if bang in bang_map:
            engine = bang_map[bang]
            # If query is empty, navigate to the search engine homepage
            if not query:
                engine_urls = {
                    'Google': 'https://www.google.com',
                    'DuckDuckGo': 'https://duckduckgo.com',
                    'Bing': 'https://www.bing.com',
                    'Yahoo': 'https://search.yahoo.com',
                    'Yandex': 'https://yandex.com',
                    'Ecosia': 'https://www.ecosia.org',
                    'Brave': 'https://search.brave.com'
                }
                return engine_urls.get(engine, 'https://www.google.com'), False
            return self.get_search_url(query, engine), True
        
        # Unknown bang, search with default engine
        return self.get_search_url(text), True
    
    def add_custom_engine(self, name, url_template):
        """Add a custom search engine"""
        if '{}' not in url_template:
            return False
        
        self._custom_engines[name] = url_template
        self._save_custom_engines()
        return True
    
    def remove_custom_engine(self, name):
        """Remove a custom search engine"""
        if name in self._custom_engines:
            del self._custom_engines[name]
            self._save_custom_engines()
            
            # Reset to default if removed engine was current
            if self.current_engine == name:
                self.current_engine = DEFAULT_SEARCH_ENGINE
            
            return True
        return False
    
    def get_custom_engines(self):
        """Get custom search engines only"""
        return dict(self._custom_engines)
    
    def get_suggestions(self, query):
        """Get search suggestions (stub for future implementation)"""
        # This could be implemented with Google/DuckDuckGo suggestion API
        return []
    
    def get_engine_icon_url(self, name=None):
        """Get favicon URL for a search engine"""
        if name is None:
            name = self.current_engine
        
        engine_domains = {
            'Google': 'https://www.google.com',
            'DuckDuckGo': 'https://duckduckgo.com',
            'Bing': 'https://www.bing.com',
            'Yahoo': 'https://search.yahoo.com',
            'Yandex': 'https://yandex.com',
            'Ecosia': 'https://www.ecosia.org',
            'Brave': 'https://search.brave.com'
        }
        
        domain = engine_domains.get(name)
        if domain:
            return f"{domain}/favicon.ico"
        return None
