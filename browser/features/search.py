import logging

from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from ..utils.constants import APP_NAME, APP_ORGANIZATION, SEARCH_ENGINES, DEFAULT_SEARCH_ENGINE
from ..utils.helpers import normalize_url, url_encode

log = logging.getLogger(__name__)


class SearchManager(QObject):
    _instance = None

    search_engine_changed = pyqtSignal(str)

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

        self.BANG_COMMANDS = {
            '!g': 'Google', '!d': 'DuckDuckGo', '!b': 'Bing',
            '!y': 'Yandex', '!w': 'Wikipedia', '!yt': 'YouTube',
        }

    def _load_custom_engines(self):
        import json
        data = self.settings.value("search/custom_engines", "")
        if data:
            try:
                self._custom_engines = json.loads(data)
            except (json.JSONDecodeError, ValueError):
                self._custom_engines = {}

    def _save_custom_engines(self):
        import json
        self.settings.setValue("search/custom_engines", json.dumps(self._custom_engines))

    @property
    def current_engine(self):
        return self.settings.value("search/engine", DEFAULT_SEARCH_ENGINE)

    @current_engine.setter
    def current_engine(self, name):
        if name in SEARCH_ENGINES or name in self._custom_engines:
            self.settings.setValue("search/engine", name)
            self.search_engine_changed.emit(name)

    def get_search_url(self, query, engine=None):
        engine = engine or self.current_engine
        template = SEARCH_ENGINES.get(engine) or self._custom_engines.get(engine)
        if template:
            encoded = url_encode(query)
            return template.replace('{}', encoded)
        default_template = SEARCH_ENGINES.get(DEFAULT_SEARCH_ENGINE, '')
        return default_template.replace('{}', url_encode(query))

    def process_input(self, text):
        text = text.strip()
        if not text:
            return None, False

        for bang, engine in self.BANG_COMMANDS.items():
            if text.startswith(bang + ' '):
                query = text[len(bang) + 1:].strip()
                if query:
                    return self.get_search_url(query, engine), True
                return None, False

        normalized = normalize_url(text)
        if self._looks_like_url(text):
            return normalized, False

        return self.get_search_url(text), True

    def _looks_like_url(self, text):
        if text.startswith(('http://', 'https://', 'ftp://', 'file://')):
            return True
        if '.' in text and ' ' not in text:
            parts = text.split('.')
            if len(parts) >= 2 and len(parts[-1]) >= 2:
                return True
        if text.startswith('localhost') or text.startswith('127.') or text.startswith('[::1]'):
            return True
        return False

    def get_available_engines(self):
        engines = dict(SEARCH_ENGINES)
        engines.update(self._custom_engines)
        return engines

    def add_custom_engine(self, name, url_template):
        if '{}' not in url_template:
            return False
        self._custom_engines[name] = url_template
        self._save_custom_engines()
        return True

    def remove_custom_engine(self, name):
        if name in self._custom_engines:
            del self._custom_engines[name]
            self._save_custom_engines()
            if self.current_engine == name:
                self.current_engine = DEFAULT_SEARCH_ENGINE
            return True
        return False

    def get_suggestions(self, query):
        if not query or len(query) < 2:
            return []
        return []
