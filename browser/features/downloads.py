import os
import json
import uuid
import logging
import mimetypes
from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSignal, QSettings, QUrl, QStandardPaths
from PyQt5.QtWebEngineWidgets import QWebEngineDownloadItem
from ..utils.constants import APP_NAME, APP_ORGANIZATION
from ..utils.helpers import format_file_size, sanitize_filename

log = logging.getLogger(__name__)


class DownloadEntry:
    def __init__(self, filename, url, path, download_id=None,
                 total_bytes=0, received_bytes=0, status='pending',
                 started_at=None, completed_at=None, mime_type=''):
        self.id = download_id or str(uuid.uuid4())
        self.filename = filename
        self.url = url
        self.path = path
        self.total_bytes = total_bytes
        self.received_bytes = received_bytes
        self.status = status
        self.started_at = started_at or datetime.now().isoformat()
        self.completed_at = completed_at
        self.mime_type = mime_type
        self._qt_download = None

    @property
    def progress(self):
        if self.total_bytes > 0:
            return int((self.received_bytes / self.total_bytes) * 100)
        return 0

    @property
    def size_text(self):
        if self.total_bytes > 0:
            return f"{format_file_size(self.received_bytes)} / {format_file_size(self.total_bytes)}"
        return format_file_size(self.received_bytes)

    @property
    def is_complete(self):
        return self.status == 'completed'

    def to_dict(self):
        return {
            'id': self.id, 'filename': self.filename, 'url': self.url,
            'path': self.path, 'total_bytes': self.total_bytes,
            'received_bytes': self.received_bytes, 'status': self.status,
            'started_at': self.started_at, 'completed_at': self.completed_at,
            'mime_type': self.mime_type,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            filename=data['filename'], url=data['url'], path=data['path'],
            download_id=data.get('id'), total_bytes=data.get('total_bytes', 0),
            received_bytes=data.get('received_bytes', 0),
            status=data.get('status', 'completed'),
            started_at=data.get('started_at'), completed_at=data.get('completed_at'),
            mime_type=data.get('mime_type', ''),
        )


class DownloadManager(QObject):
    _instance = None

    download_started = pyqtSignal(object)
    download_progress = pyqtSignal(object)
    download_completed = pyqtSignal(object)
    download_failed = pyqtSignal(object)
    download_cancelled = pyqtSignal(object)
    downloads_changed = pyqtSignal()

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
        self._downloads = {}
        self._active_downloads = {}
        self._load()

    def _load(self):
        data = self.settings.value("downloads/history", "")
        if data:
            try:
                items = json.loads(data)
                for d in items:
                    entry = DownloadEntry.from_dict(d)
                    self._downloads[entry.id] = entry
            except (json.JSONDecodeError, KeyError):
                log.warning("İndirme geçmişi okunamadı")

    def _save(self):
        items = list(self._downloads.values())
        items.sort(key=lambda x: x.started_at or '', reverse=True)
        items = items[:100]
        data = [d.to_dict() for d in items]
        self.settings.setValue("downloads/history", json.dumps(data, ensure_ascii=False))

    def _ensure_extension(self, filename, mime_type):
        _, ext = os.path.splitext(filename)
        if ext:
            return filename
        guessed = mimetypes.guess_extension(mime_type, strict=False) if mime_type else None
        if guessed:
            if guessed == '.jpe':
                guessed = '.jpg'
            return filename + guessed
        return filename

    def handle_download(self, qt_download):
        mime_type = qt_download.mimeType() if hasattr(qt_download, 'mimeType') else ''
        raw_name = qt_download.suggestedFileName() or "download"
        filename = sanitize_filename(self._ensure_extension(raw_name, mime_type))
        download_dir = ''
        if hasattr(qt_download, 'downloadDirectory'):
            download_dir = qt_download.downloadDirectory()
        if not download_dir:
            download_dir = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        download_path = os.path.join(download_dir, filename)

        if hasattr(qt_download, 'setDownloadFileName'):
            qt_download.setDownloadFileName(filename)
        elif hasattr(qt_download, 'setPath'):
            qt_download.setPath(download_path)

        entry = DownloadEntry(
            filename=filename,
            url=qt_download.url().toString(),
            path=download_path,
            total_bytes=qt_download.totalBytes(),
            mime_type=mime_type,
        )
        entry.status = 'downloading'
        entry._qt_download = qt_download

        self._downloads[entry.id] = entry
        self._active_downloads[entry.id] = qt_download

        qt_download.downloadProgress.connect(
            lambda recv, total, e=entry: self._on_progress(e, recv, total)
        )
        qt_download.stateChanged.connect(
            lambda state, e=entry: self._on_state_changed(e, state)
        )

        qt_download.accept()
        self.download_started.emit(entry)
        self.downloads_changed.emit()
        self._save()
        return entry

    def _on_progress(self, entry, received, total):
        entry.received_bytes = received
        if total > 0:
            entry.total_bytes = total
        self.download_progress.emit(entry)
        self.downloads_changed.emit()

    def _on_state_changed(self, entry, state):
        if state == QWebEngineDownloadItem.DownloadCompleted:
            entry.status = 'completed'
            entry.completed_at = datetime.now().isoformat()
            self._active_downloads.pop(entry.id, None)
            self.download_completed.emit(entry)
        elif state == QWebEngineDownloadItem.DownloadCancelled:
            entry.status = 'cancelled'
            self._active_downloads.pop(entry.id, None)
            self.download_cancelled.emit(entry)
        elif state == QWebEngineDownloadItem.DownloadInterrupted:
            entry.status = 'failed'
            self._active_downloads.pop(entry.id, None)
            self.download_failed.emit(entry)
        self._save()
        self.downloads_changed.emit()

    def cancel_download(self, download_id):
        qt_dl = self._active_downloads.get(download_id)
        if qt_dl:
            qt_dl.cancel()
            return True
        return False

    def pause_download(self, download_id):
        qt_dl = self._active_downloads.get(download_id)
        if qt_dl and hasattr(qt_dl, 'pause'):
            qt_dl.pause()
            entry = self._downloads.get(download_id)
            if entry:
                entry.status = 'paused'
            return True
        return False

    def resume_download(self, download_id):
        qt_dl = self._active_downloads.get(download_id)
        if qt_dl and hasattr(qt_dl, 'resume'):
            qt_dl.resume()
            entry = self._downloads.get(download_id)
            if entry:
                entry.status = 'downloading'
            return True
        return False

    def remove_download(self, download_id):
        self._active_downloads.pop(download_id, None)
        if download_id in self._downloads:
            del self._downloads[download_id]
            self._save()
            self.downloads_changed.emit()
            return True
        return False

    def open_file(self, download_id):
        entry = self._downloads.get(download_id)
        if not entry or entry.status != 'completed':
            log.warning("Download not found or not completed: %s", download_id)
            return False
        file_path = entry.path
        # Try to resolve path if it doesn't exist directly
        if not os.path.exists(file_path):
            # Try download directory + filename
            download_dir = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
            alt_path = os.path.join(download_dir, entry.filename)
            if os.path.exists(alt_path):
                file_path = alt_path
            else:
                log.warning("Downloaded file not found: %s", file_path)
                return False
        try:
            os.startfile(file_path)
            return True
        except OSError as e:
            log.error("Failed to open file %s: %s", file_path, e)
            return False

    def open_folder(self, download_id):
        entry = self._downloads.get(download_id)
        if entry and os.path.exists(os.path.dirname(entry.path)):
            os.startfile(os.path.dirname(entry.path))
            return True
        return False

    def get_download(self, download_id):
        return self._downloads.get(download_id)

    def get_all_downloads(self):
        items = list(self._downloads.values())
        items.sort(key=lambda x: x.started_at or '', reverse=True)
        return items

    def get_active_downloads(self):
        return [d for d in self._downloads.values() if d.status == 'downloading']

    def get_completed_downloads(self):
        return [d for d in self._downloads.values() if d.status == 'completed']

    def clear_completed(self):
        to_remove = [d_id for d_id, d in self._downloads.items() if d.status in ('completed', 'cancelled', 'failed')]
        for d_id in to_remove:
            del self._downloads[d_id]
        self._save()
        self.downloads_changed.emit()

    def clear_all(self):
        for qt_dl in self._active_downloads.values():
            qt_dl.cancel()
        self._active_downloads.clear()
        self._downloads.clear()
        self._save()
        self.downloads_changed.emit()

    def get_download_count(self):
        return len(self._downloads)

    def get_active_count(self):
        return len(self._active_downloads)
