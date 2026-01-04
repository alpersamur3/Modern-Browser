"""
History Manager for Modern Browser
"""

import json
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from ..utils.constants import APP_NAME, APP_ORGANIZATION, MAX_HISTORY_ITEMS


class HistoryEntry:
    """Represents a single history entry"""
    
    def __init__(self, url, title, timestamp=None, visit_count=1):
        self.url = url
        self.title = title
        self.timestamp = timestamp or datetime.now().isoformat()
        self.visit_count = visit_count
        self.favicon = None
    
    def to_dict(self):
        return {
            'url': self.url,
            'title': self.title,
            'timestamp': self.timestamp,
            'visit_count': self.visit_count,
            'favicon': self.favicon
        }
    
    @classmethod
    def from_dict(cls, data):
        entry = cls(
            url=data.get('url', ''),
            title=data.get('title', ''),
            timestamp=data.get('timestamp'),
            visit_count=data.get('visit_count', 1)
        )
        entry.favicon = data.get('favicon')
        return entry


class HistoryManager(QObject):
    """Manages browsing history with persistence"""
    
    # Signals
    history_added = pyqtSignal(object)  # HistoryEntry
    history_removed = pyqtSignal(str)  # url
    history_cleared = pyqtSignal()
    history_changed = pyqtSignal()
    
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
        self.history = {}  # url -> HistoryEntry
        self._load()
    
    def _load(self):
        """Load history from storage"""
        history_json = self.settings.value("history/entries", "[]")
        try:
            history_data = json.loads(history_json)
            for entry_data in history_data:
                entry = HistoryEntry.from_dict(entry_data)
                self.history[entry.url] = entry
        except (json.JSONDecodeError, TypeError):
            self.history = {}
    
    def _save(self):
        """Save history to storage"""
        # Limit history size
        entries = sorted(
            self.history.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )[:MAX_HISTORY_ITEMS]
        
        self.history = {entry.url: entry for entry in entries}
        
        history_data = [entry.to_dict() for entry in entries]
        self.settings.setValue("history/entries", json.dumps(history_data))
    
    def add_entry(self, url, title, favicon=None):
        """Add or update a history entry"""
        # Skip internal pages
        if url.startswith(('about:', 'chrome:', 'browser:', 'data:')):
            return None
        
        if url in self.history:
            # Update existing entry
            entry = self.history[url]
            entry.title = title or entry.title
            entry.timestamp = datetime.now().isoformat()
            entry.visit_count += 1
            if favicon:
                entry.favicon = favicon
        else:
            # Create new entry
            entry = HistoryEntry(url, title)
            if favicon:
                entry.favicon = favicon
            self.history[url] = entry
        
        self._save()
        self.history_added.emit(entry)
        self.history_changed.emit()
        return entry
    
    def remove_entry(self, url):
        """Remove a single history entry"""
        if url in self.history:
            del self.history[url]
            self._save()
            self.history_removed.emit(url)
            self.history_changed.emit()
            return True
        return False
    
    def remove_entries_by_domain(self, domain):
        """Remove all entries from a domain"""
        urls_to_remove = [
            url for url in self.history.keys()
            if domain in url
        ]
        for url in urls_to_remove:
            del self.history[url]
        
        if urls_to_remove:
            self._save()
            self.history_changed.emit()
        
        return len(urls_to_remove)
    
    def get_entry(self, url):
        """Get a history entry by URL"""
        return self.history.get(url)
    
    def get_all_entries(self):
        """Get all history entries sorted by timestamp"""
        return sorted(
            self.history.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )
    
    def get_recent_entries(self, limit=50):
        """Get recent history entries"""
        entries = self.get_all_entries()
        return entries[:limit]
    
    def get_today_entries(self):
        """Get today's history entries"""
        today = datetime.now().date()
        return [
            entry for entry in self.history.values()
            if datetime.fromisoformat(entry.timestamp).date() == today
        ]
    
    def get_yesterday_entries(self):
        """Get yesterday's history entries"""
        yesterday = (datetime.now() - timedelta(days=1)).date()
        return [
            entry for entry in self.history.values()
            if datetime.fromisoformat(entry.timestamp).date() == yesterday
        ]
    
    def get_this_week_entries(self):
        """Get this week's history entries"""
        week_ago = datetime.now() - timedelta(days=7)
        return [
            entry for entry in self.history.values()
            if datetime.fromisoformat(entry.timestamp) > week_ago
        ]
    
    def get_this_month_entries(self):
        """Get this month's history entries"""
        month_ago = datetime.now() - timedelta(days=30)
        return [
            entry for entry in self.history.values()
            if datetime.fromisoformat(entry.timestamp) > month_ago
        ]
    
    def get_most_visited(self, limit=10):
        """Get most visited sites"""
        entries = sorted(
            self.history.values(),
            key=lambda x: x.visit_count,
            reverse=True
        )
        return entries[:limit]
    
    def search(self, query):
        """Search history by title or URL"""
        query = query.lower()
        results = []
        for entry in self.history.values():
            if query in entry.title.lower() or query in entry.url.lower():
                results.append(entry)
        return sorted(results, key=lambda x: x.timestamp, reverse=True)
    
    def clear_all(self):
        """Clear all history"""
        self.history.clear()
        self._save()
        self.history_cleared.emit()
        self.history_changed.emit()
    
    def clear_range(self, start_date, end_date):
        """Clear history within a date range"""
        urls_to_remove = []
        for url, entry in self.history.items():
            entry_date = datetime.fromisoformat(entry.timestamp)
            if start_date <= entry_date <= end_date:
                urls_to_remove.append(url)
        
        for url in urls_to_remove:
            del self.history[url]
        
        if urls_to_remove:
            self._save()
            self.history_changed.emit()
        
        return len(urls_to_remove)
    
    def clear_last_hour(self):
        """Clear history from the last hour"""
        hour_ago = datetime.now() - timedelta(hours=1)
        return self.clear_range(hour_ago, datetime.now())
    
    def clear_today(self):
        """Clear today's history"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.clear_range(today_start, datetime.now())
    
    def clear_last_week(self):
        """Clear last week's history"""
        week_ago = datetime.now() - timedelta(days=7)
        return self.clear_range(week_ago, datetime.now())
    
    def get_count(self):
        """Get total history count"""
        return len(self.history)
    
    def get_grouped_by_date(self):
        """Get history grouped by date"""
        grouped = {}
        for entry in self.history.values():
            date = datetime.fromisoformat(entry.timestamp).date().isoformat()
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(entry)
        
        # Sort entries within each date
        for date in grouped:
            grouped[date].sort(key=lambda x: x.timestamp, reverse=True)
        
        return grouped
    
    def export_to_json(self, filepath):
        """Export history to JSON file"""
        entries = [entry.to_dict() for entry in self.get_all_entries()]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
    
    def import_from_json(self, filepath):
        """Import history from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            entries_data = json.load(f)
        
        for entry_data in entries_data:
            entry = HistoryEntry.from_dict(entry_data)
            if entry.url not in self.history:
                self.history[entry.url] = entry
        
        self._save()
        self.history_changed.emit()
