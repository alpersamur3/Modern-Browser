"""
Bookmark Manager for Modern Browser
"""

import json
import os
import uuid
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from ..utils.constants import APP_NAME, APP_ORGANIZATION


class Bookmark:
    """Represents a single bookmark"""
    
    def __init__(self, url, title, folder_id=None, favicon=None, id=None):
        self.id = id or str(uuid.uuid4())
        self.url = url
        self.title = title
        self.folder_id = folder_id
        self.favicon = favicon
        self.created_at = datetime.now().isoformat()
        self.visited_count = 0
        self.last_visited = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'folder_id': self.folder_id,
            'favicon': self.favicon,
            'created_at': self.created_at,
            'visited_count': self.visited_count,
            'last_visited': self.last_visited
        }
    
    @classmethod
    def from_dict(cls, data):
        bookmark = cls(
            url=data.get('url', ''),
            title=data.get('title', ''),
            folder_id=data.get('folder_id'),
            favicon=data.get('favicon'),
            id=data.get('id')
        )
        bookmark.created_at = data.get('created_at', datetime.now().isoformat())
        bookmark.visited_count = data.get('visited_count', 0)
        bookmark.last_visited = data.get('last_visited')
        return bookmark


class BookmarkFolder:
    """Represents a bookmark folder"""
    
    def __init__(self, name, parent_id=None, id=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.parent_id = parent_id
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        folder = cls(
            name=data.get('name', ''),
            parent_id=data.get('parent_id'),
            id=data.get('id')
        )
        folder.created_at = data.get('created_at', datetime.now().isoformat())
        return folder


class BookmarkManager(QObject):
    """Manages bookmarks with persistence"""
    
    # Signals
    bookmark_added = pyqtSignal(object)  # Bookmark
    bookmark_removed = pyqtSignal(str)  # bookmark id
    bookmark_updated = pyqtSignal(object)  # Bookmark
    folder_added = pyqtSignal(object)  # BookmarkFolder
    folder_removed = pyqtSignal(str)  # folder id
    bookmarks_changed = pyqtSignal()
    
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
        self.bookmarks = {}  # id -> Bookmark
        self.folders = {}  # id -> BookmarkFolder
        self._init_default_folders()
        self._load()
    
    def _init_default_folders(self):
        """Initialize default bookmark folders"""
        # Create root folders if they don't exist
        default_folders = [
            ('bookmarks_bar', 'Yer İmleri Çubuğu', None),
            ('other_bookmarks', 'Diğer Yer İmleri', None),
            ('mobile_bookmarks', 'Mobil Yer İmleri', None)
        ]
        
        for folder_id, name, parent_id in default_folders:
            if folder_id not in self.folders:
                folder = BookmarkFolder(name, parent_id, folder_id)
                self.folders[folder_id] = folder
    
    def _load(self):
        """Load bookmarks from storage"""
        # Load folders
        folders_json = self.settings.value("bookmarks/folders", "[]")
        try:
            folders_data = json.loads(folders_json)
            for folder_data in folders_data:
                folder = BookmarkFolder.from_dict(folder_data)
                self.folders[folder.id] = folder
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Ensure default folders exist
        self._init_default_folders()
        
        # Load bookmarks
        bookmarks_json = self.settings.value("bookmarks/items", "[]")
        try:
            bookmarks_data = json.loads(bookmarks_json)
            for bookmark_data in bookmarks_data:
                bookmark = Bookmark.from_dict(bookmark_data)
                self.bookmarks[bookmark.id] = bookmark
        except (json.JSONDecodeError, TypeError):
            pass
    
    def _save(self):
        """Save bookmarks to storage"""
        # Save folders (excluding default ones that are recreated)
        folders_data = [
            folder.to_dict() for folder in self.folders.values()
            if folder.id not in ['bookmarks_bar', 'other_bookmarks', 'mobile_bookmarks']
        ]
        self.settings.setValue("bookmarks/folders", json.dumps(folders_data))
        
        # Save bookmarks
        bookmarks_data = [bookmark.to_dict() for bookmark in self.bookmarks.values()]
        self.settings.setValue("bookmarks/items", json.dumps(bookmarks_data))
    
    # Bookmark operations
    def add_bookmark(self, url, title, folder_id='bookmarks_bar', favicon=None):
        """Add a new bookmark"""
        bookmark = Bookmark(url, title, folder_id, favicon)
        self.bookmarks[bookmark.id] = bookmark
        self._save()
        self.bookmark_added.emit(bookmark)
        self.bookmarks_changed.emit()
        return bookmark
    
    def remove_bookmark(self, bookmark_id):
        """Remove a bookmark"""
        if bookmark_id in self.bookmarks:
            del self.bookmarks[bookmark_id]
            self._save()
            self.bookmark_removed.emit(bookmark_id)
            self.bookmarks_changed.emit()
            return True
        return False
    
    def update_bookmark(self, bookmark_id, **kwargs):
        """Update bookmark properties"""
        if bookmark_id in self.bookmarks:
            bookmark = self.bookmarks[bookmark_id]
            for key, value in kwargs.items():
                if hasattr(bookmark, key):
                    setattr(bookmark, key, value)
            self._save()
            self.bookmark_updated.emit(bookmark)
            self.bookmarks_changed.emit()
            return bookmark
        return None
    
    def get_bookmark(self, bookmark_id):
        """Get a bookmark by ID"""
        return self.bookmarks.get(bookmark_id)
    
    def get_bookmark_by_url(self, url):
        """Get bookmark by URL"""
        for bookmark in self.bookmarks.values():
            if bookmark.url == url:
                return bookmark
        return None
    
    def is_bookmarked(self, url):
        """Check if URL is bookmarked"""
        return self.get_bookmark_by_url(url) is not None
    
    def get_bookmarks_in_folder(self, folder_id=None):
        """Get all bookmarks in a folder"""
        return [
            bookmark for bookmark in self.bookmarks.values()
            if bookmark.folder_id == folder_id
        ]
    
    def get_all_bookmarks(self):
        """Get all bookmarks"""
        return list(self.bookmarks.values())
    
    def get_bookmarks_bar(self):
        """Get bookmarks in the bookmarks bar"""
        return self.get_bookmarks_in_folder('bookmarks_bar')
    
    def move_bookmark(self, bookmark_id, folder_id):
        """Move bookmark to a different folder"""
        return self.update_bookmark(bookmark_id, folder_id=folder_id)
    
    def visit_bookmark(self, bookmark_id):
        """Update bookmark visit statistics"""
        if bookmark_id in self.bookmarks:
            bookmark = self.bookmarks[bookmark_id]
            bookmark.visited_count += 1
            bookmark.last_visited = datetime.now().isoformat()
            self._save()
    
    # Folder operations
    def add_folder(self, name, parent_id=None):
        """Add a new bookmark folder"""
        folder = BookmarkFolder(name, parent_id)
        self.folders[folder.id] = folder
        self._save()
        self.folder_added.emit(folder)
        self.bookmarks_changed.emit()
        return folder
    
    def remove_folder(self, folder_id):
        """Remove a folder and its contents"""
        if folder_id in ['bookmarks_bar', 'other_bookmarks', 'mobile_bookmarks']:
            return False  # Can't remove default folders
        
        if folder_id in self.folders:
            # Remove all bookmarks in folder
            bookmarks_to_remove = [
                b.id for b in self.bookmarks.values() if b.folder_id == folder_id
            ]
            for bookmark_id in bookmarks_to_remove:
                del self.bookmarks[bookmark_id]
            
            # Remove subfolders recursively
            subfolders = [f.id for f in self.folders.values() if f.parent_id == folder_id]
            for subfolder_id in subfolders:
                self.remove_folder(subfolder_id)
            
            # Remove folder
            del self.folders[folder_id]
            self._save()
            self.folder_removed.emit(folder_id)
            self.bookmarks_changed.emit()
            return True
        return False
    
    def rename_folder(self, folder_id, new_name):
        """Rename a folder"""
        if folder_id in self.folders:
            self.folders[folder_id].name = new_name
            self._save()
            self.bookmarks_changed.emit()
            return True
        return False
    
    def get_folder(self, folder_id):
        """Get a folder by ID"""
        return self.folders.get(folder_id)
    
    def get_subfolders(self, parent_id=None):
        """Get subfolders of a folder"""
        return [
            folder for folder in self.folders.values()
            if folder.parent_id == parent_id
        ]
    
    def get_all_folders(self):
        """Get all folders"""
        return list(self.folders.values())
    
    # Search
    def search(self, query):
        """Search bookmarks by title or URL"""
        query = query.lower()
        results = []
        for bookmark in self.bookmarks.values():
            if query in bookmark.title.lower() or query in bookmark.url.lower():
                results.append(bookmark)
        return results
    
    # Import/Export
    def export_to_html(self, filepath):
        """Export bookmarks to HTML format"""
        html = ['<!DOCTYPE NETSCAPE-Bookmark-file-1>']
        html.append('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">')
        html.append('<TITLE>Bookmarks</TITLE>')
        html.append('<H1>Bookmarks</H1>')
        html.append('<DL><p>')
        
        def export_folder(folder_id, indent=1):
            folder = self.folders.get(folder_id)
            if folder:
                html.append('    ' * indent + f'<DT><H3>{folder.name}</H3>')
                html.append('    ' * indent + '<DL><p>')
            
            for bookmark in self.get_bookmarks_in_folder(folder_id):
                html.append('    ' * (indent + 1) + 
                           f'<DT><A HREF="{bookmark.url}">{bookmark.title}</A>')
            
            for subfolder in self.get_subfolders(folder_id):
                export_folder(subfolder.id, indent + 1)
            
            if folder:
                html.append('    ' * indent + '</DL><p>')
        
        export_folder('bookmarks_bar')
        export_folder('other_bookmarks')
        html.append('</DL><p>')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html))
    
    def import_from_html(self, filepath):
        """Import bookmarks from HTML format"""
        # Basic HTML bookmark parser
        import re
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all bookmark links
        pattern = r'<A HREF="([^"]+)"[^>]*>([^<]+)</A>'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        for url, title in matches:
            if not self.is_bookmarked(url):
                self.add_bookmark(url, title)
    
    def clear_all(self):
        """Clear all bookmarks"""
        self.bookmarks.clear()
        # Keep default folders
        custom_folders = [
            f_id for f_id in self.folders.keys()
            if f_id not in ['bookmarks_bar', 'other_bookmarks', 'mobile_bookmarks']
        ]
        for folder_id in custom_folders:
            del self.folders[folder_id]
        self._save()
        self.bookmarks_changed.emit()
