"""
Download Manager for Modern Browser
"""

import os
import json
import uuid
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QSettings, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineDownloadItem
from ..utils.constants import APP_NAME, APP_ORGANIZATION
from ..utils.helpers import (
    format_file_size, sanitize_filename, generate_unique_filename,
    get_file_extension
)


class DownloadItem:
    """Represents a single download"""
    
    STATUS_PENDING = 'pending'
    STATUS_DOWNLOADING = 'downloading'
    STATUS_PAUSED = 'paused'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_FAILED = 'failed'
    
    def __init__(self, url, filename, path, total_size=0):
        self.id = str(uuid.uuid4())
        self.url = url
        self.filename = filename
        self.path = path
        self.total_size = total_size
        self.downloaded_size = 0
        self.status = self.STATUS_PENDING
        self.started_at = datetime.now().isoformat()
        self.completed_at = None
        self.speed = 0
        self.error_message = None
        self._download_item = None
    
    @property
    def progress(self):
        if self.total_size == 0:
            return 0
        return int((self.downloaded_size / self.total_size) * 100)
    
    @property
    def full_path(self):
        return os.path.join(self.path, self.filename)
    
    @property
    def size_text(self):
        if self.total_size == 0:
            return f"{format_file_size(self.downloaded_size)}"
        return f"{format_file_size(self.downloaded_size)} / {format_file_size(self.total_size)}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'filename': self.filename,
            'path': self.path,
            'total_size': self.total_size,
            'downloaded_size': self.downloaded_size,
            'status': self.status,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data):
        item = cls(
            url=data.get('url', ''),
            filename=data.get('filename', ''),
            path=data.get('path', ''),
            total_size=data.get('total_size', 0)
        )
        item.id = data.get('id', str(uuid.uuid4()))
        item.downloaded_size = data.get('downloaded_size', 0)
        item.status = data.get('status', cls.STATUS_PENDING)
        item.started_at = data.get('started_at')
        item.completed_at = data.get('completed_at')
        item.error_message = data.get('error_message')
        return item


class DownloadManager(QObject):
    """Manages file downloads"""
    
    # Signals
    download_started = pyqtSignal(object)  # DownloadItem
    download_progress = pyqtSignal(object)  # DownloadItem
    download_completed = pyqtSignal(object)  # DownloadItem
    download_failed = pyqtSignal(object)  # DownloadItem
    download_cancelled = pyqtSignal(object)  # DownloadItem
    downloads_changed = pyqtSignal()
    
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
        self.downloads = {}  # id -> DownloadItem
        self.active_downloads = {}  # id -> QWebEngineDownloadItem
        self._load()
    
    def _load(self):
        """Load download history from storage"""
        downloads_json = self.settings.value("downloads/history", "[]")
        try:
            downloads_data = json.loads(downloads_json)
            for download_data in downloads_data:
                item = DownloadItem.from_dict(download_data)
                self.downloads[item.id] = item
        except (json.JSONDecodeError, TypeError):
            self.downloads = {}
    
    def _save(self):
        """Save download history to storage"""
        # Save last 100 downloads
        downloads = sorted(
            self.downloads.values(),
            key=lambda x: x.started_at,
            reverse=True
        )[:100]
        
        downloads_data = [d.to_dict() for d in downloads]
        self.settings.setValue("downloads/history", json.dumps(downloads_data))
    
    def get_download_path(self):
        """Get the default download path"""
        from PyQt5.QtCore import QStandardPaths
        return self.settings.value(
            "downloads/path",
            QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        )
    
    def set_download_path(self, path):
        """Set the default download path"""
        self.settings.setValue("downloads/path", path)
    
    def handle_download(self, download_item):
        """Handle a new download request from WebEngine"""
        url = download_item.url().toString()
        suggested_filename = download_item.suggestedFileName()
        
        # Sanitize filename
        filename = sanitize_filename(suggested_filename)
        
        # Get download path
        path = self.get_download_path()
        
        # Generate unique filename
        filename = generate_unique_filename(path, filename)
        
        # Create download item
        item = DownloadItem(
            url=url,
            filename=filename,
            path=path,
            total_size=download_item.totalBytes()
        )
        item._download_item = download_item
        item.status = DownloadItem.STATUS_DOWNLOADING
        
        # Set download path
        download_item.setPath(item.full_path)
        
        # Connect signals
        download_item.downloadProgress.connect(
            lambda received, total: self._on_progress(item.id, received, total)
        )
        download_item.finished.connect(
            lambda: self._on_finished(item.id)
        )
        
        # Accept download
        download_item.accept()
        
        # Store
        self.downloads[item.id] = item
        self.active_downloads[item.id] = download_item
        self._save()
        
        self.download_started.emit(item)
        self.downloads_changed.emit()
        
        return item
    
    def _on_progress(self, download_id, received, total):
        """Handle download progress update"""
        if download_id in self.downloads:
            item = self.downloads[download_id]
            item.downloaded_size = received
            if total > 0:
                item.total_size = total
            self.download_progress.emit(item)
    
    def _on_finished(self, download_id):
        """Handle download completion"""
        if download_id not in self.downloads:
            return
        
        item = self.downloads[download_id]
        
        if download_id in self.active_downloads:
            download_item = self.active_downloads[download_id]
            
            if download_item.state() == QWebEngineDownloadItem.DownloadCompleted:
                item.status = DownloadItem.STATUS_COMPLETED
                item.completed_at = datetime.now().isoformat()
                self.download_completed.emit(item)
            elif download_item.state() == QWebEngineDownloadItem.DownloadCancelled:
                item.status = DownloadItem.STATUS_CANCELLED
                self.download_cancelled.emit(item)
            elif download_item.state() == QWebEngineDownloadItem.DownloadInterrupted:
                item.status = DownloadItem.STATUS_FAILED
                item.error_message = "Download interrupted"
                self.download_failed.emit(item)
            
            del self.active_downloads[download_id]
        
        self._save()
        self.downloads_changed.emit()
    
    def pause_download(self, download_id):
        """Pause a download"""
        if download_id in self.active_downloads:
            self.active_downloads[download_id].pause()
            if download_id in self.downloads:
                self.downloads[download_id].status = DownloadItem.STATUS_PAUSED
            self.downloads_changed.emit()
            return True
        return False
    
    def resume_download(self, download_id):
        """Resume a paused download"""
        if download_id in self.active_downloads:
            self.active_downloads[download_id].resume()
            if download_id in self.downloads:
                self.downloads[download_id].status = DownloadItem.STATUS_DOWNLOADING
            self.downloads_changed.emit()
            return True
        return False
    
    def cancel_download(self, download_id):
        """Cancel a download"""
        if download_id in self.active_downloads:
            self.active_downloads[download_id].cancel()
            return True
        return False
    
    def remove_download(self, download_id):
        """Remove a download from history"""
        if download_id in self.downloads:
            # Cancel if active
            if download_id in self.active_downloads:
                self.active_downloads[download_id].cancel()
                del self.active_downloads[download_id]
            
            del self.downloads[download_id]
            self._save()
            self.downloads_changed.emit()
            return True
        return False
    
    def open_file(self, download_id):
        """Open a downloaded file"""
        if download_id in self.downloads:
            item = self.downloads[download_id]
            if item.status == DownloadItem.STATUS_COMPLETED:
                import subprocess
                import platform
                
                filepath = item.full_path
                if os.path.exists(filepath):
                    if platform.system() == 'Darwin':
                        subprocess.call(('open', filepath))
                    elif platform.system() == 'Windows':
                        os.startfile(filepath)
                    else:
                        subprocess.call(('xdg-open', filepath))
                    return True
        return False
    
    def open_folder(self, download_id):
        """Open the containing folder"""
        if download_id in self.downloads:
            item = self.downloads[download_id]
            import subprocess
            import platform
            
            folder = item.path
            if os.path.exists(folder):
                if platform.system() == 'Darwin':
                    subprocess.call(('open', folder))
                elif platform.system() == 'Windows':
                    subprocess.call(('explorer', folder))
                else:
                    subprocess.call(('xdg-open', folder))
                return True
        return False
    
    def get_download(self, download_id):
        """Get a download by ID"""
        return self.downloads.get(download_id)
    
    def get_all_downloads(self):
        """Get all downloads sorted by start time"""
        return sorted(
            self.downloads.values(),
            key=lambda x: x.started_at,
            reverse=True
        )
    
    def get_active_downloads(self):
        """Get currently active downloads"""
        return [
            self.downloads[id] for id in self.active_downloads.keys()
            if id in self.downloads
        ]
    
    def get_completed_downloads(self):
        """Get completed downloads"""
        return [
            d for d in self.downloads.values()
            if d.status == DownloadItem.STATUS_COMPLETED
        ]
    
    def clear_completed(self):
        """Clear completed downloads from history"""
        completed = [
            d.id for d in self.downloads.values()
            if d.status in [DownloadItem.STATUS_COMPLETED, 
                           DownloadItem.STATUS_CANCELLED,
                           DownloadItem.STATUS_FAILED]
        ]
        for download_id in completed:
            del self.downloads[download_id]
        
        self._save()
        self.downloads_changed.emit()
    
    def clear_all(self):
        """Clear all downloads"""
        # Cancel active downloads
        for download_item in list(self.active_downloads.values()):
            download_item.cancel()
        
        self.active_downloads.clear()
        self.downloads.clear()
        self._save()
        self.downloads_changed.emit()
    
    def get_active_count(self):
        """Get number of active downloads"""
        return len(self.active_downloads)
    
    def get_total_count(self):
        """Get total number of downloads in history"""
        return len(self.downloads)
