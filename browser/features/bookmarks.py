import json
import os
import uuid
from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from ..utils.constants import APP_NAME, APP_ORGANIZATION

import logging
log = logging.getLogger(__name__)


class BookmarkEntry:
    def __init__(self, url, title, folder_id="bookmarks_bar", bookmark_id=None,
                 favicon_url="", created_at=None, tags=None):
        self.id = bookmark_id or str(uuid.uuid4())
        self.url = url
        self.title = title
        self.folder_id = folder_id
        self.favicon_url = favicon_url
        self.created_at = created_at or datetime.now().isoformat()
        self.tags = tags or []

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'folder_id': self.folder_id,
            'favicon_url': self.favicon_url,
            'created_at': self.created_at,
            'tags': self.tags,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            url=data['url'],
            title=data['title'],
            folder_id=data.get('folder_id', 'bookmarks_bar'),
            bookmark_id=data.get('id'),
            favicon_url=data.get('favicon_url', ''),
            created_at=data.get('created_at'),
            tags=data.get('tags', []),
        )


class BookmarkFolder:
    def __init__(self, name, folder_id=None, parent_id=None):
        self.id = folder_id or str(uuid.uuid4())
        self.name = name
        self.parent_id = parent_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            folder_id=data.get('id'),
            parent_id=data.get('parent_id'),
        )


class BookmarkManager(QObject):
    _instance = None

    bookmark_added = pyqtSignal(object)
    bookmark_removed = pyqtSignal(str)
    bookmark_updated = pyqtSignal(object)
    folder_added = pyqtSignal(object)
    folder_removed = pyqtSignal(str)
    bookmarks_changed = pyqtSignal()

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
        self._bookmarks = {}
        self._folders = {}
        self._init_default_folders()
        self._load()

    def _init_default_folders(self):
        defaults = [
            BookmarkFolder("Yer İmleri Çubuğu", "bookmarks_bar"),
            BookmarkFolder("Diğer Yer İmleri", "other_bookmarks"),
        ]
        for folder in defaults:
            if folder.id not in self._folders:
                self._folders[folder.id] = folder

    def _load(self):
        data = self.settings.value("bookmarks/data", "")
        if data:
            try:
                parsed = json.loads(data)
                for b in parsed.get('bookmarks', []):
                    entry = BookmarkEntry.from_dict(b)
                    self._bookmarks[entry.id] = entry
                for f in parsed.get('folders', []):
                    folder = BookmarkFolder.from_dict(f)
                    self._folders[folder.id] = folder
            except (json.JSONDecodeError, KeyError):
                log.warning("Yer imleri verisi okunamadı")

    def _save(self):
        data = {
            'bookmarks': [b.to_dict() for b in self._bookmarks.values()],
            'folders': [f.to_dict() for f in self._folders.values()],
        }
        self.settings.setValue("bookmarks/data", json.dumps(data, ensure_ascii=False))

    def add_bookmark(self, url, title, folder_id="bookmarks_bar", tags=None):
        entry = BookmarkEntry(url, title, folder_id, tags=tags)
        self._bookmarks[entry.id] = entry
        self._save()
        self.bookmark_added.emit(entry)
        self.bookmarks_changed.emit()
        return entry

    def remove_bookmark(self, bookmark_id):
        if bookmark_id in self._bookmarks:
            del self._bookmarks[bookmark_id]
            self._save()
            self.bookmark_removed.emit(bookmark_id)
            self.bookmarks_changed.emit()
            return True
        return False

    def update_bookmark(self, bookmark_id, **kwargs):
        if bookmark_id not in self._bookmarks:
            return False
        entry = self._bookmarks[bookmark_id]
        allowed = {'url', 'title', 'folder_id', 'favicon_url', 'tags'}
        for key, value in kwargs.items():
            if key in allowed:
                setattr(entry, key, value)
        self._save()
        self.bookmark_updated.emit(entry)
        self.bookmarks_changed.emit()
        return True

    def get_bookmark(self, bookmark_id):
        return self._bookmarks.get(bookmark_id)

    def get_bookmark_by_url(self, url):
        for b in self._bookmarks.values():
            if b.url == url:
                return b
        return None

    def is_bookmarked(self, url):
        return self.get_bookmark_by_url(url) is not None

    def get_bookmarks_in_folder(self, folder_id):
        return [b for b in self._bookmarks.values() if b.folder_id == folder_id]

    def get_all_bookmarks(self):
        return list(self._bookmarks.values())

    def search_bookmarks(self, query):
        q = query.lower()
        return [
            b for b in self._bookmarks.values()
            if q in b.title.lower() or q in b.url.lower() or any(q in t.lower() for t in b.tags)
        ]

    def add_folder(self, name, parent_id=None):
        folder = BookmarkFolder(name, parent_id=parent_id)
        self._folders[folder.id] = folder
        self._save()
        self.folder_added.emit(folder)
        self.bookmarks_changed.emit()
        return folder

    def remove_folder(self, folder_id):
        if folder_id in ('bookmarks_bar', 'other_bookmarks'):
            return False
        if folder_id in self._folders:
            for b_id in [b.id for b in self._bookmarks.values() if b.folder_id == folder_id]:
                del self._bookmarks[b_id]
            del self._folders[folder_id]
            self._save()
            self.folder_removed.emit(folder_id)
            self.bookmarks_changed.emit()
            return True
        return False

    def get_folder(self, folder_id):
        return self._folders.get(folder_id)

    def get_all_folders(self):
        return list(self._folders.values())

    def get_bookmark_count(self):
        return len(self._bookmarks)

    def export_bookmarks_html(self, filepath):
        lines = ['<!DOCTYPE NETSCAPE-Bookmark-file-1>', '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
                 '<TITLE>Bookmarks</TITLE>', '<H1>Bookmarks</H1>', '<DL><p>']
        for folder in self._folders.values():
            lines.append(f'  <DT><H3>{folder.name}</H3>')
            lines.append('  <DL><p>')
            for b in self.get_bookmarks_in_folder(folder.id):
                lines.append(f'    <DT><A HREF="{b.url}">{b.title}</A>')
            lines.append('  </DL><p>')
        lines.append('</DL><p>')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def import_bookmarks_html(self, filepath):
        import re
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        links = re.findall(r'<A HREF="([^"]+)"[^>]*>([^<]+)</A>', content, re.IGNORECASE)
        count = 0
        for url, title in links:
            if not self.is_bookmarked(url):
                self.add_bookmark(url, title.strip())
                count += 1
        return count
