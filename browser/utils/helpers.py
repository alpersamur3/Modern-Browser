import os
import re
import hashlib
import logging
from datetime import datetime
from urllib.parse import urlparse, quote, unquote
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon, QColor
from .constants import RESOURCES_DIR, ICONS_DIR

log = logging.getLogger(__name__)


def get_resource_path(*parts):
    return os.path.join(RESOURCES_DIR, *parts)


def get_icon_path(name: str) -> str:
    return os.path.join(ICONS_DIR, name)


def load_icon(name: str, color: str = None) -> QIcon:
    path = get_icon_path(name)
    if not os.path.exists(path):
        return QIcon()
    if color is None:
        return QIcon(path)
    with open(path, 'r', encoding='utf-8') as f:
        svg_data = f.read()
    svg_data = svg_data.replace('stroke="currentColor"', f'stroke="{color}"')
    svg_data = svg_data.replace("stroke='currentColor'", f"stroke='{color}'")
    from PyQt5.QtSvg import QSvgRenderer
    from PyQt5.QtGui import QPixmap, QPainter
    from PyQt5.QtCore import QByteArray
    renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
    pixmap = QPixmap(24, 24)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def load_themed_icon(name: str, dark_mode: bool) -> QIcon:
    color = '#e0e0e0' if dark_mode else '#444444'
    return load_icon(name, color)


def is_valid_url(url_string: str) -> bool:
    try:
        result = urlparse(url_string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def normalize_url(url_string: str):
    url_string = url_string.strip()
    if " " in url_string or not ("." in url_string or url_string.startswith("localhost")):
        return None
    if not url_string.startswith(("http://", "https://", "file://", "about:")):
        url_string = "https://" + url_string
    return url_string


def extract_domain(url_string: str) -> str:
    try:
        parsed = urlparse(url_string)
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except ValueError:
        return url_string


def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024
        i += 1
    return f"{size:.2f} {size_names[i]}"


def format_timestamp(timestamp, format_str: str = "%d.%m.%Y %H:%M") -> str:
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            return timestamp
    return timestamp.strftime(format_str)


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"


def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    filename = re.sub(r"\s+", " ", filename).strip()
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200 - len(ext)] + ext
    return filename or "download"


def generate_unique_filename(directory: str, filename: str) -> str:
    if not os.path.exists(os.path.join(directory, filename)):
        return filename
    name, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(directory, f"{name} ({counter}){ext}")):
        counter += 1
    return f"{name} ({counter}){ext}"


def get_favicon_url(url_string: str):
    try:
        parsed = urlparse(url_string)
        return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
    except ValueError:
        return None


def is_internal_page(url) -> bool:
    if isinstance(url, QUrl):
        url = url.toString()
    return url.startswith(("about:", "chrome:", "browser:", "data:"))


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_file_extension(url_or_path: str) -> str:
    try:
        parsed = urlparse(url_or_path)
        path = parsed.path if parsed.path else url_or_path
        _, ext = os.path.splitext(path)
        return ext.lower()
    except ValueError:
        return ""


def mime_type_to_extension(mime_type: str) -> str:
    mime_map = {
        "text/html": ".html", "text/plain": ".txt", "text/css": ".css",
        "application/javascript": ".js", "application/json": ".json",
        "application/pdf": ".pdf", "application/zip": ".zip",
        "image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif",
        "image/webp": ".webp", "image/svg+xml": ".svg",
        "video/mp4": ".mp4", "video/webm": ".webm",
        "audio/mpeg": ".mp3", "audio/wav": ".wav",
    }
    return mime_map.get(mime_type, "")


def escape_html(text: str) -> str:
    table = {"&": "&amp;", '"': "&quot;", "'": "&#39;", ">": "&gt;", "<": "&lt;"}
    return "".join(table.get(c, c) for c in text)


def url_encode(text: str) -> str:
    return quote(text, safe="")


def url_decode(text: str) -> str:
    return unquote(text)
