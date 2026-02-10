import json
import logging
from datetime import datetime, timedelta

from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from ..utils.constants import APP_NAME, APP_ORGANIZATION, MAX_HISTORY_ITEMS

log = logging.getLogger(__name__)


class HistoryEntry:
    def __init__(self, url, title, visit_count=1, last_visit=None):
        self.url = url
        self.title = title
        self.visit_count = visit_count
        self.last_visit = last_visit or datetime.now().isoformat()

    def to_dict(self):
        return {
            'url': self.url,
            'title': self.title,
            'visit_count': self.visit_count,
            'last_visit': self.last_visit,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            url=data['url'],
            title=data['title'],
            visit_count=data.get('visit_count', 1),
            last_visit=data.get('last_visit'),
        )


class HistoryManager(QObject):
    _instance = None

    history_added = pyqtSignal(object)
    history_removed = pyqtSignal(str)
    history_cleared = pyqtSignal()
    history_changed = pyqtSignal()

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
        self._entries = {}
        self._load()

    def _load(self):
        data = self.settings.value("history/data", "")
        if data:
            try:
                items = json.loads(data)
                for item in items:
                    entry = HistoryEntry.from_dict(item)
                    self._entries[entry.url] = entry
            except (json.JSONDecodeError, KeyError):
                log.warning("Geçmiş verisi okunamadı")

    def _save(self):
        entries = sorted(self._entries.values(), key=lambda e: e.last_visit, reverse=True)
        entries = entries[:MAX_HISTORY_ITEMS]
        data = [e.to_dict() for e in entries]
        self.settings.setValue("history/data", json.dumps(data, ensure_ascii=False))

    def add_entry(self, url, title):
        if not url or url in ('about:blank', ''):
            return None
        if url in self._entries:
            entry = self._entries[url]
            entry.visit_count += 1
            entry.last_visit = datetime.now().isoformat()
            entry.title = title or entry.title
        else:
            entry = HistoryEntry(url, title)
            self._entries[url] = entry
        self._save()
        self.history_added.emit(entry)
        self.history_changed.emit()
        return entry

    def remove_entry(self, url):
        if url in self._entries:
            del self._entries[url]
            self._save()
            self.history_removed.emit(url)
            self.history_changed.emit()
            return True
        return False

    def get_entry(self, url):
        return self._entries.get(url)

    def get_all_entries(self):
        entries = list(self._entries.values())
        entries.sort(key=lambda e: e.last_visit, reverse=True)
        return entries

    def get_recent_entries(self, limit=50):
        return self.get_all_entries()[:limit]

    def search_history(self, query):
        q = query.lower()
        results = [
            e for e in self._entries.values()
            if q in e.title.lower() or q in e.url.lower()
        ]
        results.sort(key=lambda e: e.last_visit, reverse=True)
        return results

    def get_most_visited(self, limit=10):
        entries = list(self._entries.values())
        entries.sort(key=lambda e: e.visit_count, reverse=True)
        return entries[:limit]

    def get_entries_by_date(self, start_date, end_date=None):
        if end_date is None:
            end_date = datetime.now()
        results = []
        for entry in self._entries.values():
            try:
                visit_time = datetime.fromisoformat(entry.last_visit)
                if start_date <= visit_time <= end_date:
                    results.append(entry)
            except (ValueError, TypeError):
                continue
        results.sort(key=lambda e: e.last_visit, reverse=True)
        return results

    def get_today_entries(self):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_entries_by_date(today)

    def get_yesterday_entries(self):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        return self.get_entries_by_date(yesterday, today)

    def get_this_week_entries(self):
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_entries_by_date(week_start)

    def clear_all(self):
        self._entries.clear()
        self._save()
        self.history_cleared.emit()
        self.history_changed.emit()

    def clear_range(self, hours=None, days=None):
        if hours:
            cutoff = datetime.now() - timedelta(hours=hours)
        elif days:
            cutoff = datetime.now() - timedelta(days=days)
        else:
            return
        to_remove = []
        for url, entry in self._entries.items():
            try:
                visit_time = datetime.fromisoformat(entry.last_visit)
                if visit_time >= cutoff:
                    to_remove.append(url)
            except (ValueError, TypeError):
                continue
        for url in to_remove:
            del self._entries[url]
        self._save()
        self.history_changed.emit()

    def get_entry_count(self):
        return len(self._entries)

    def export_history(self, filepath):
        data = [e.to_dict() for e in self.get_all_entries()]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def import_history(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        count = 0
        for item in data:
            entry = HistoryEntry.from_dict(item)
            if entry.url not in self._entries:
                self._entries[entry.url] = entry
                count += 1
        self._save()
        self.history_changed.emit()
        return count
